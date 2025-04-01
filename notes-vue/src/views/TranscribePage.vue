<template>
  <div class="step-container view-padding">
    <h2>3. 字幕解析</h2>
    <p class="info">处理 Video ID: {{ store.videoId || 'N/A' }}</p>

    <div v-if="store.isLoadingTranscribe" class="status-indicator loading">
      <span class="spinner">🎙️</span> 正在解析字幕...
    </div>

    <div v-if="store.errorMessage && !store.isTranscribeComplete" class="error-message">
      解析失败：{{ store.errorMessage }}
      <div class="action-buttons">
        <button @click="goBackHome">返回首页</button>
      </div>
    </div>

    <div v-if="store.isTranscribeComplete && !store.errorMessage" class="transcription-result">
      <h3>✅ 解析完成</h3>
      <pre class="transcript-output">{{ store.rawTranscript }}</pre>
      <div class="action-buttons">
        <button @click="startGeneration" :disabled="store.isLoadingGenerate">
          <span v-if="store.isLoadingGenerate">处理中...</span>
          <span v-else>生成内容</span>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { useProcessingStore } from '@/stores/processing';
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';

const store = useProcessingStore();
const router = useRouter();

function startGeneration() {
  // Model selection could be added here if needed before calling generate
  store.generateMarkdownContent(store.selectedAiModel); // Action handles navigation
}

function goBackHome() {
  store.resetState();
  router.push({ name: 'InputPage' });
}

// Ensure state is valid on mount
onMounted(() => {
  if (!store.videoId || !store.isDownloadComplete) {
    console.warn("TranscribePage mounted without download completion. Redirecting.");
    // Try to redirect intelligently based on state
    router.replace(store.videoUrl ? { name: 'DownloadPage' } : { name: 'InputPage' });
  }
});
</script>

<style scoped> /* Adapt styles from DownloadPage */
.view-padding { padding: 2em; }
.step-container { max-width: 80%; margin: 2em auto; border: 1px solid #eee; border-radius: 8px; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
h2 { margin-bottom: 0.5em; text-align: center;}
.info { color: #666; margin-bottom: 1.5em; text-align: center;}
.status-indicator { padding: 1.5em; border-radius: 6px; margin: 1em auto; font-size: 1.1em; display: flex; align-items: center; justify-content: center; gap: 10px; text-align: center; width: fit-content; }
.loading { background-color: #e3f2fd; border: 1px solid #bbdefb; color: #0d47a1; }
.error-message { margin-top: 1em; color: #D8000C; background-color: #FFD2D2; border: 1px solid #D8000C; padding: 15px; border-radius: 4px; text-align: center; }
.transcription-result { margin-top: 1.5em; padding: 1em; }
.transcription-result h3 { text-align: center; color: green; margin-bottom: 1em; }
.transcript-output { background-color: #f8f8f8; border: 1px solid #e0e0e0; padding: 1em; border-radius: 4px; white-space: pre-wrap; word-wrap: break-word; max-height: 300px; overflow-y: auto; font-size: 0.95em; line-height: 1.5; font-family: monospace; margin-bottom: 1.5em; }
.action-buttons { margin-top: 1.5em; text-align: center; }
button { padding: 0.8em 1.5em; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
button:disabled { background-color: #cccccc; cursor: not-allowed; }
.error-message button { background-color: #6c757d; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.spinner { display: inline-block; animation: spin 1.5s linear infinite; font-size: 1.2em; }
</style>