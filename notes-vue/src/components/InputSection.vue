<script setup>
import {computed, ref} from 'vue';
import { defineEmits } from 'vue';

const emit = defineEmits(['process']);
const urlInput = ref('');
const showValidationError = ref(false);
const fileInputRef = ref(null); // Ref for the file input element

// --- NEW: State for Dropdowns ---
// Options for Subtitle Models
const subtitleModelOptions = ref([
  { value: 'whispercpp_medium', text: 'Whisper.cpp (Medium)' },
  { value: 'whispercpp_base', text: 'Whisper.cpp (Base)' },
  { value: 'whispercpp_small', text: 'Whisper.cpp (Small)' },
  { value: 'fasterwhisper_tiny', text: 'FasterWhisper (tiny)' },
  // Add other options supported by your backend, e.g.:
  // { value: 'faster_whisper_base', text: 'Faster Whisper (Base)' },
  // { value: 'cloud_asr_standard', text: 'Cloud ASR (Standard)' },
]);
const selectedSubtitleModel = ref(subtitleModelOptions.value[0].value); // Default to the first option

// Options for LLM Models
const llmModelOptions = ref([
  { value: 'deepseek-coder', text: "DeepSeek coder"},
  { value: 'gpt-4', text: 'GPT-4' },
  { value: 'claude-3-sonnet', text: 'Claude 3 Sonnet' },
  { value: 'glm-4v', text: 'GLM-4V' },
  { value: 'other', text: "其他模型"},
  // Add other options supported by your backend, e.g.:
  // { value: 'claude-3-opus', text: 'Claude 3 Opus' },
  // { value: 'local_llama3', text: 'Local Llama 3' },
]);
const selectedLlmModel = ref(llmModelOptions.value[0].value); // Default to the first option


const isValidUrl = computed(() => {
  if (!urlInput.value) return false;
  try { new URL(urlInput.value); return true; } catch (_) { return false; }
});

function processUrl() {
  if(!isValidUrl.value) {
    showValidationError.value = !isValidUrl.value;
    emit('process', {type: 'url', value: "", 'subtitle_model': selectedSubtitleModel.value, 'llm_model': selectedLlmModel.value});
    return;
  }
  if (isValidUrl.value && urlInput.value.trim()) {
    showValidationError.value =false;
    emit('process', {type: 'url', value: urlInput.value.trim(), 'subtitle_model': selectedSubtitleModel.value, 'llm_model': selectedLlmModel.value});
  }
}

function selectFile() {
  // Trigger click on the hidden file input
  fileInputRef.value?.click();
}

function handleFileChange(event) {
  const file = event.target.files?.[0];
  if (file) {
    emit('process', {type: 'file', value: file});
  }
  // Reset file input value so the same file can be selected again if needed
  event.target.value = null;
}
</script>

<template>
  <div class="input-section">
<!--    <input type="text" v-model="urlInput" placeholder="Enter video URL (e.g., YouTube, Bilibili...)"/>-->
    <input
        type="text"
        v-model="urlInput"
        placeholder="输入视频URL (例如 https://www.bilibili.com/video/xxx)"
    />
    <button @click="processUrl" :disabled="$attrs.isLoading">搜索/下载</button>
    <span>/</span>
    <button @click="selectFile" :disabled="$attrs.isLoading">上传文件</button>
    <!-- Hidden file input -->
    <input type="file" ref="fileInputRef" @change="handleFileChange" accept="video/*,audio/*" style="display: none;">
  </div>
  <div class="model-p-area">
    <p class="highlight">注意：大文件和外网下载文件尽量下载本地后上传</p>
  </div>
  <!-- NEW: Dropdown Selection Area -->
  <div class="model-selection-area">
    <div class="select-group">
      <label for="subtitle-model">字幕解析模型:</label>
      <select id="subtitle-model" v-model="selectedSubtitleModel" :disabled="isLoading">
        <option v-for="option in subtitleModelOptions" :key="option.value" :value="option.value">
          {{ option.text }}
        </option>
      </select>
    </div>
    <div class="select-group">
      <label for="llm-model">笔记生成模型:</label>
      <select id="llm-model" v-model="selectedLlmModel" :disabled="isLoading">
        <option v-for="option in llmModelOptions" :key="option.value" :value="option.value">
          {{ option.text }}
        </option>
      </select>
    </div>
  </div>
  <!--  <p v-if="showValidationError" class="error-text">请输入有效的 URL。</p>-->
</template>

<style scoped>
.input-section {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

input[type="text"] {
  flex-grow: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  min-width: 250px;
}

button {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #0056b3;
}

span {
  margin: 0 5px;
  color: #555;
}

.error-text { color: red; font-size: 0.9em; }
.error-message { margin-top: 1em; color: #D8000C; background-color: #FFD2D2; border: 1px solid #D8000C; padding: 10px; border-radius: 4px; text-align: center; }

.model-p-area {
  display: flex;
  justify-content: center;
  //gap: 30px; /* Space between dropdown groups */
  //margin-top: 20px; /* Space below input section */
  //margin-bottom: 25px; /* Space above progress/results */
  //padding: 15px;
  //background-color: #f8f9fa; /* Light background */
  //border-radius: 6px;
  flex-wrap: wrap; /* Allow wrapping on smaller screens */
}
.highlight {
  font-weight: bold; /* 加粗 */
  //color: red;        /* 标红 */
}

/* --- NEW: Styles for Dropdown Area --- */
.model-selection-area {
  display: flex;
  justify-content: center;
  gap: 30px; /* Space between dropdown groups */
  margin-top: 20px; /* Space below input section */
  margin-bottom: 25px; /* Space above progress/results */
  padding: 15px;
  background-color: #f8f9fa; /* Light background */
  border-radius: 6px;
  flex-wrap: wrap; /* Allow wrapping on smaller screens */
}
.select-group {
  display: flex;
  align-items: center;
  gap: 8px; /* Space between label and select */
}
.select-group label {
  font-weight: 500;
  font-size: 0.9em;
  color: #555;
}
.select-group select {
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  min-width: 150px; /* Give dropdowns some width */
  background-color: white;
}
.select-group select:disabled {
  background-color: #e9ecef; /* Indicate disabled state */
  cursor: not-allowed;
}
</style>