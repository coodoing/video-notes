<script setup>
import { ref, computed, onUnmounted, nextTick } from 'vue';
import axios from 'axios';
import InputSection from './components/InputSection.vue';
import VideoPlayer from './components/VideoPlayer.vue';
import TranscriptViewer from './components/TranscriptViewer.vue';
import SummaryViewer from './components/SummaryViewer.vue';

const backendUrlBase = 'http://localhost:8000'; // Base URL for backend (HTTP)
const backendApiUrl = `${backendUrlBase}/api`;    // API endpoint base
// 动态构建WebSocket URL
const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const backendHost = window.location.hostname;
const wsUrl = `${wsProtocol}${backendHost}:8000/api/ws/process`; // Adjust port if backend is elsewhere
console.log("WebSocket URL:", wsUrl); // Log for debugging

// --- Component State ---
const ProcessingState = {
  IDLE: 'idle',
  UPLOADING: 'uploading',
  CONNECTING: 'connecting',
  PROCESSING: 'processing',
  SUCCESS: 'success',
  ERROR: 'error',
};
const currentState = ref(ProcessingState.IDLE); // Track the overall state
const processingUpdates = ref([]); // Array to store { stage, message, status } logs
const lastError = ref(null);     // Store the last critical error object { stage, message }
const finalResult = ref(null);   // Holds the final data object on success

const currentTab = ref('watch');
const videoCurrentTime = ref(0);
const videoPlayerRef = ref(null);
const progressListRef = ref(null); // Ref for the progress list container

let socket = null; // To hold the WebSocket instance

// --- Computed Properties ---
const isLoading = computed(() => [
  ProcessingState.UPLOADING,
  ProcessingState.CONNECTING,
  ProcessingState.PROCESSING
].includes(currentState.value));

const showResults = computed(() => currentState.value === ProcessingState.SUCCESS && finalResult.value);

const finalStatusMessage = computed(() => {
  if (currentState.value === ProcessingState.SUCCESS) {
    return "音视频处理成功!";
  }
  if (currentState.value === ProcessingState.ERROR && lastError.value) {
    return `音视频处理失败，[${lastError.value.stage}]: ${lastError.value.message}`;
  }
  return ""; // No final status otherwise
});

// Computed properties for result data (remain the same)
const transcript = computed(() => finalResult.value?.transcript || []);
const videoSourceUrl = computed(() => {
  if (!finalResult.value?.video_source_url) return '';
  const url = finalResult.value.video_source_url;
  // const url = 'http://localhost:8000/video/robot.mp4';//外部cdn存储服务器/本地存储 'http://localhost:8080/robot.mp4';
  // Prepend backend base URL ONLY if it's a relative path served by backend static files
  if (url.startsWith('/static/')) {
    return `${backendUrlBase}${url}`;
  }
  return url;
});
const briefSummary = computed(() => finalResult.value?.brief_summary || '');
const detailedSummary = computed(() => finalResult.value?.detailed_summary || '');

// --- WebSocket/SSE处理逻辑 ---
function cleanupWebSocket() {
  if (socket) {
    // Remove listeners to prevent potential issues after close
    socket.onopen = null;
    socket.onmessage = null;
    socket.onerror = null;
    socket.onclose = null;
    if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
      socket.close();
      console.log("客户端关闭WebSocket.");
    }
    socket = null;
  }
}

function resetState() {
  currentState.value = ProcessingState.IDLE;
  processingUpdates.value = [];
  lastError.value = null;
  finalResult.value = null;
  currentTab.value = 'watch'; // Reset tab
  cleanupWebSocket(); // Ensure previous socket is closed
}

// Function to add updates and scroll the progress list
function addProgressUpdate(update) {
  processingUpdates.value.push(update);
  // Scroll progress list to bottom
  nextTick(() => {
    const listEl = progressListRef.value;
    if (listEl) {
      listEl.scrollTop = listEl.scrollHeight;
    }
  });
}

// Extracted function to set up WebSocket connection and handlers
function setupWebSocketConnection(startMessage) {
  addProgressUpdate({ stage: 'connect', message: '连接后台服务...', status: 'processing' });
  currentState.value = ProcessingState.CONNECTING;

  try {
    socket = new WebSocket(wsUrl);
  } catch (error) {
    console.error("WebSocket创建失败:", error);
    handleProcessingError('connect', `WebSocket初始化失败: ${error.message}`);
    return; // Stop if WebSocket object cannot be created
  }


  socket.onopen = () => {
    console.log("WebSocket连接成功.");
    addProgressUpdate({ stage: 'connect', message: 'WebSocket连接成功，开始处理...', status: 'success' });
    currentState.value = ProcessingState.PROCESSING; // Move to processing state
    try {
      socket.send(JSON.stringify(startMessage));
    } catch(sendError) {
      console.error("WebSocket发送消息失败:", sendError);
      handleProcessingError('connect', `发送消息失败: ${sendError.message}`);
    }
  };

  //SSE实现，eventSource.onmessage = (event) => {
  socket.onmessage = (event) => {
    console.log("WebSocket接收后端消息:", event.data);
    let update;
    try {
      update = JSON.parse(event.data);
      if (typeof update !== 'object' || update === null || !update.status) {
        throw new Error("消息为空或格式异常.");
      }
    } catch (e) {
      console.error("非JSON格式消息:", event.data, e);
      addProgressUpdate({ stage: 'ws_receive', message: `非JSON格式消息: ${e.message}`, status: 'error' });
      // Decide if this error is critical enough to stop processing
      // handleProcessingError('ws_receive', 'Received malformed update from server.');
      return; // Continue listening for potentially valid messages unless critical
    }

    // Add valid update to log
    addProgressUpdate(update);

    // Handle final states signaled by the backend message
    if (update.status === 'complete') {
      finalResult.value = update.data || {}; // Store the final payload
      currentState.value = ProcessingState.SUCCESS;
      console.log("消息处理成功.");
      cleanupWebSocket(); // Close connection on successful completion
    } else if (update.status === 'error') {
      handleProcessingError(update.stage || 'processing', update.message);
      // Backend signaled an error, we should stop and cleanup
      cleanupWebSocket();
    }
    // If status is 'processing' or 'success' (for intermediate steps), just log it (already done)
  };

  socket.onerror = (error) => {
    // This often fires just before onclose when there's an issue.
    console.error("WebSocket异常事件:", error);
    // Don't set the final error state here, wait for onclose for definitive termination state
    addProgressUpdate({ stage: 'connection', message: 'WebSocket连接错误.', status: 'error' });
  };

  socket.onclose = (event) => {
    console.log("WebSocket连接关闭:", event.code, event.reason, event.wasClean);
    // Only transition to ERROR state if we weren't already in SUCCESS or ERROR
    if (currentState.value !== ProcessingState.SUCCESS && currentState.value !== ProcessingState.ERROR) {
      handleProcessingError(
          'connection',
          `连接异常关闭 (Code: ${event.code})${event.reason ? ' Reason: ' + event.reason : ''}`
      );
    } else if (currentState.value === ProcessingState.SUCCESS) {
      addProgressUpdate({ stage: 'connection', message: '连接关闭成功.', status: 'success' });
    }
    // Ensure state reflects non-processing if closed
    if (isLoading.value) {
      currentState.value = ProcessingState.ERROR; // Assume error if closed while loading/processing
    }
  };
}

// Centralized error handling
function handleProcessingError(stage, message) {
  console.error(`处理异常 - Stage: ${stage}, Message: ${message}`);
  // Avoid setting error if already successfully completed
  if (currentState.value !== ProcessingState.SUCCESS) {
    lastError.value = { stage, message };
    currentState.value = ProcessingState.ERROR;
    addProgressUpdate({ stage: stage, message: message, status: 'error' }); // Log the error too
    cleanupWebSocket(); // Ensure connection is closed on error
  }
}

// Main function triggered by InputSection
async function handleProcessRequest({ type, value, subtitle_model, llm_model }) {
  resetState(); // Start clean

  let startMessage = null;

  try {
    // --- Prepare base start message ---
    const baseMessage = {
      type: type,
      value: null, // Will be set below
      // ADD selected models to the message payload
      subtitle_model: null, //selectedSubtitleModel.value,
      llm_model: null, //selectedLlmModel.value
    };

    if (type === 'url') {
      if(value === '') {
        throw new Error("非法格式url");
      }
      baseMessage.value = value; // Value is the URL string
      baseMessage.subtitle_model = subtitle_model
      baseMessage.llm_model = llm_model
      startMessage = baseMessage;
    } else if (type === 'file') {
      // --- File Upload Step ---
      currentState.value = ProcessingState.UPLOADING;
      addProgressUpdate({ stage: 'upload', message: '上传文件中...', status: 'processing' });
      const formData = new FormData();
      formData.append('file', value); // 'value' is the File object
      try {
        const uploadResponse = await axios.post(`${backendApiUrl}/upload/file`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        const fileId = uploadResponse.data.file_id;
        if (!fileId) throw new Error("后台服务未返回可用file_id.");
        addProgressUpdate({ stage: 'upload', message: `文件上传成功 (ID: ${fileId}).`, status: 'success' });
        baseMessage.value = fileId; // Value is the uploaded file ID
        startMessage = baseMessage;
      } catch (uploadError) {
        console.error("文件上传失败:", uploadError);
        const errorMsg = uploadError.response?.data?.detail || uploadError.message;
        handleProcessingError('upload', errorMsg); // Use centralized error handler
        return; // Stop processing
      }
      // --- End File Upload Step ---

    } else {
      throw new Error("请求格式错误（非url和文件）");
    }

    // If we have a valid message (URL processed or File uploaded), start WebSocket
    if (startMessage) {
      setupWebSocketConnection(startMessage);
    } else {
      // This case should ideally not be reached if logic above is sound
      handleProcessingError('setup', 'WebSocket setup阶段请求处理异常.');
    }

  } catch (err) {
    console.error("WebSocket setup阶段请求处理异常:", err);
    handleProcessingError('初始化异常', err.message);
  }
}

// --- Video Player Interaction ---
function updateVideoTime(time) {
  videoCurrentTime.value = time;
}

function seekVideo(time) {
  videoPlayerRef.value?.seek(time);
  currentTab.value = 'watch';
}

// --- Lifecycle Hook ---
onUnmounted(() => {
  cleanupWebSocket(); // Ensure cleanup when component is destroyed
});

</script>

<template>
  <div class="app-container">
    <h1>NotesAI</h1>

    <InputSection :is-loading="isLoading" @process="handleProcessRequest" />

    <!-- Progress Indicator Area -->
    <!--    <div v-if="currentState !== ProcessingState.IDLE && currentState !== ProcessingState.SUCCESS" class="progress-container">-->
    <div v-if="currentState !== ProcessingState.IDLE" class="progress-container">
      <h2>实时处理流程:</h2>
      <ul ref="progressListRef" class="progress-log">
        <li v-for="(update, index) in processingUpdates" :key="index" :class="`status-${update.status}`">
          <span class="stage-tag">[{{ update.stage }}]</span> {{ update.message }}
        </li>
      </ul>
      <!-- Optional spinner during active processing -->
      <div v-if="isLoading" class="spinner" aria-label="Processing..."></div>
    </div>

    <!-- Final Status Message Area -->
    <div v-if="finalStatusMessage"
         :class="['final-status', currentState === ProcessingState.SUCCESS ? 'status-success' : 'status-error']">
      {{ finalStatusMessage }}
    </div>

    <!-- Results Area (Show only on successful completion) -->
    <div v-if="showResults" class="results-container">
      <!-- Tabs -->
      <div class="tabs">
        <button @click="currentTab = 'watch'" :class="{ active: currentTab === 'watch' }">视频展示</button>
        <button @click="currentTab = 'subtitles'" :class="{ active: currentTab === 'subtitles' }">字幕内容
        </button>
        <button @click="currentTab = 'brief'" :class="{ active: currentTab === 'brief' }">主题大纲</button>
        <button @click="currentTab = 'detailed'" :class="{ active: currentTab === 'detailed' }">笔记
        </button>
<!--        <button @click="currentTab = 'notes'" :class="{ active: currentTab === 'notes' }">生成笔记-->
<!--        </button>-->
        <!-- Add other tabs like 'Article Generation', 'AI Q&A' -->
      </div>

      <!-- Content Area -->
      <div class="content-area">
        <div v-show="currentTab === 'watch'" class="video-section">
          <VideoPlayer
              ref="videoPlayerRef"
              :src="videoSourceUrl"
              @timeupdate="updateVideoTime"
          />
          <TranscriptViewer
              :transcript="transcript"
              :current-time="videoCurrentTime"
              @seek="seekVideo"
              :interactive="true"
              class="transcript-sidebar"
          />
        </div>
        <!-- Other tab content using computed properties -->
        <div v-if="currentTab === 'subtitles'">
          <h2>字幕内容：</h2>
          <TranscriptViewer
              :transcript="transcript"
              :current-time="videoCurrentTime"
              @seek="seekVideo"
              :interactive="true" />
        </div>

        <div v-if="currentTab === 'brief'">
          <h2>描述信息</h2>
          <SummaryViewer :summary="briefSummary"/>
        </div>

        <div v-if="currentTab === 'detailed'">
          <h2>生成笔记</h2>
          <SummaryViewer :summary="detailedSummary || '笔记暂不可用'"/>
        </div>

<!--        <div v-if="currentTab === 'notes'">-->
<!--          <h2>生成笔记</h2>-->
<!--          <SummaryViewer :summary="notesSummary"/>-->
<!--        </div>-->
      </div>
    </div>
  </div>
</template>

<style>
/* Add basic styling for layout, tabs, etc. */
body { font-family: sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
.app-container { max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
h1 { text-align: center; color: #333; }

/* Progress Indicator Styles */
.progress-container {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
  margin-bottom: 15px; /* Space before final status or results */
}
.progress-container h2 { margin-top: 0; font-size: 1.1em; color: #333; }
.progress-log {
  list-style: none;
  padding: 0 0 10px 0; /* Add padding at bottom */
  margin: 0;
  max-height: 250px; /* Limit height */
  overflow-y: auto; /* Add scroll */
  border-bottom: 1px solid #eee; /* Separate from spinner */
  margin-bottom: 10px; /* Space before spinner */
}
.progress-log li {
  padding: 4px 2px;
  font-size: 0.9em;
  border-bottom: 1px dashed #eee;
  line-height: 1.4;
}
.progress-log li:last-child { border-bottom: none; }
.stage-tag {
  display: inline-block;
  min-width: 80px; /* Adjust as needed */
  margin-right: 8px;
  font-weight: bold;
  text-transform: capitalize;
  color: #444;
}
.status-processing .stage-tag { color: #555; }
.status-success .stage-tag { color: #28a745; }
.status-error .stage-tag { color: #dc3545; }
.status-complete .stage-tag { color: #007bff; } /* Can use for final 'complete' stage */

.status-processing { color: #555; }
.status-success { color: #28a745; }
.status-error { color: #dc3545; font-weight: bold; }
.status-complete { color: #007bff; font-weight: bold; }

.spinner { /* Simple CSS spinner */
  border: 4px solid #f3f3f3; /* Light grey */
  border-top: 4px solid #3498db; /* Blue */
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
  margin: 10px auto 0;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Final Status Message */
.final-status {
  text-align: center;
  padding: 15px;
  border: 1px solid;
  border-radius: 4px;
  margin-top: 15px;
  margin-bottom: 15px;
  font-weight: bold;
}
.final-status.status-success { background-color: #d4edda; color: #155724; border-color: #c3e6cb; }
.final-status.status-error { background-color: #f8d7da; color: #721c24; border-color: #f5c6cb; }

/* Error Message (Fallback/General, can be removed if Final Status covers all) */
/* .error-message { text-align: center; padding: 15px; background-color: #ffebee; color: #c62828; border: 1px solid #ef9a9a; border-radius: 4px; margin-top: 15px; } */

/* Results Area & Tabs */
.results-container { margin-top: 20px; }
.tabs { display: flex; border-bottom: 1px solid #ccc; margin-bottom: 20px; flex-wrap: wrap; }
.tabs button { padding: 10px 15px; border: none; background: none; cursor: pointer; font-size: 1em; margin-right: 5px; border-bottom: 3px solid transparent; white-space: nowrap;}
.tabs button.active { border-bottom-color: #007bff; font-weight: bold; }
.tabs button:hover:not(.active) { background-color: #eee; }
.content-area { }

/* Video Section Layout */
.video-section { display: flex; gap: 20px; align-items: flex-start; }
.video-section > :first-child { flex: 3; max-width: 70%; } /* Video Player */
.transcript-sidebar { flex: 1; max-height: 400px; overflow-y: auto; border-left: 1px solid #eee; padding-left: 15px; }

/* Responsive */
@media (max-width: 768px) {
  .video-section { flex-direction: column; }
  .video-section > :first-child, .transcript-sidebar { max-width: 100%; flex: none; width: 100%; }
  .transcript-sidebar { margin-top: 15px; border-left: none; padding-left: 0; max-height: 300px; }
}
</style>

<!--<template>-->
<!--  <img alt="Vue logo" src="./assets/notes.png" />-->
<!--  <main>-->
<!--    <RouterView v-slot="{ Component }">-->
<!--      <transition name="fade" mode="out-in">-->
<!--        <component :is="Component" />-->
<!--      </transition>-->
<!--    </RouterView>-->
<!--  </main>-->
<!--</template>-->

<!--<script>-->
<!--export default {-->
<!--  name: "App",-->
<!--  components: {-->
<!--  },-->
<!--};-->
<!--</script>-->

<!--<style>-->
<!--#app {-->
<!--  font-family: Avenir, Helvetica, Arial, sans-serif;-->
<!--  -webkit-font-smoothing: antialiased;-->
<!--  -moz-osx-font-smoothing: grayscale;-->
<!--  text-align: center;-->
<!--  color: #2c3e50;-->
<!--  margin-top: 60px;-->
<!--}-->
<!--main {-->
<!--  padding: 20px;-->
<!--}-->
<!--</style>-->
