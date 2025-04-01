<template>
  <div class="step-container view-padding">
    <h2>2. 视频下载</h2>
    <p class="info">处理 URL: {{ store.videoUrl || 'N/A' }}</p>

    <div v-if="store.isLoadingDownload" class="status-indicator loading">
      <span class="spinner">⏳</span> 正在下载视频...
    </div>

    <div v-if="store.errorMessage && !store.isDownloadComplete" class="error-message">
      下载失败：{{ store.errorMessage }}
      <div class="action-buttons">
        <button @click="goBackHome">返回首页</button>
      </div>
    </div>

    <div v-if="store.isDownloadComplete && !store.errorMessage" class="status-indicator success">
      ✅ 下载完成！
      <div class="action-buttons">
        <button @click="startTranscription" :disabled="store.isLoadingTranscribe">
          <span v-if="store.isLoadingTranscribe">处理中...</span>
          <span v-else>解析字幕</span>
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

function startTranscription() {
  store.transcribeVideo(); // Action handles navigation
}

function goBackHome() {
  store.resetState();
  router.push({ name: 'InputPage' });
}

// Ensure state is valid on mount (guard should handle most, but good practice)
onMounted(() => {
  if (!store.videoUrl) {
    console.warn("DownloadPage mounted without videoUrl in store. Redirecting.");
    goBackHome();
  }
});
</script>

<style scoped> /* Basic Styles */
.view-padding { padding: 2em; }
.step-container { max-width: 80%; margin: 2em auto; border: 1px solid #eee; border-radius: 8px; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }
h2 { margin-bottom: 0.5em; }
.info { color: #666; margin-bottom: 1.5em; word-break: break-all; }
.status-indicator { padding: 1.5em; border-radius: 6px; margin-top: 1em; font-size: 1.1em; display: flex; align-items: center; justify-content: center; gap: 10px; }
.loading { background-color: #e3f2fd; border: 1px solid #bbdefb; color: #0d47a1; }
.success { background-color: #e8f5e9; border: 1px solid #c8e6c9; color: #1b5e20; flex-direction: column; } /* Stack button below text */
.error-message { margin-top: 1em; color: #D8000C; background-color: #FFD2D2; border: 1px solid #D8000C; padding: 15px; border-radius: 4px; }
.action-buttons { margin-top: 1.5em; }
button { padding: 0.8em 1.5em; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
button:disabled { background-color: #cccccc; cursor: not-allowed; }
.error-message button { background-color: #6c757d; } /* Different color for error actions */
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.spinner { display: inline-block; animation: spin 1.5s linear infinite; font-size: 1.2em; }
</style>