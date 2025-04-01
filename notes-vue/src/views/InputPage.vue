<template>
  <div class="input-container view-padding">
    <h2>1. 输入视频链接</h2>
    <div class="input-group">
      <input
          type="url"
          v-model="localVideoUrl"
          placeholder="输入视频 URL (例如 https://www.bilibili.com/video/BV1HG411X78x)"
          :disabled="store.isLoadingDownload"
          @keyup.enter="startDownload"
      />
      <button @click="startDownload" :disabled="!isValidUrl || store.isLoadingDownload">
        <span v-if="store.isLoadingDownload">处理中...</span>
        <span v-else>搜索 / 下载</span>
      </button>
    </div>
    <p v-if="showValidationError" class="error-text">请输入有效的 URL。</p>
    <!-- Display errors relevant to this view (e.g., if download failed immediately) -->
    <div v-if="store.errorMessage && !store.isDownloadComplete && !store.isLoadingDownload" class="error-message">
      处理失败：{{ store.errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useProcessingStore } from '@/stores/processing';

const store = useProcessingStore();
const localVideoUrl = ref('');
const showValidationError = ref(false);

const isValidUrl = computed(() => {
  if (!localVideoUrl.value) return false;
  try { new URL(localVideoUrl.value); return true; } catch (_) { return false; }
});

function startDownload() {
  if (!isValidUrl.value || store.isLoadingDownload) {
    showValidationError.value = !isValidUrl.value; return;
  }
  showValidationError.value = false;
  store.downloadVideo(localVideoUrl.value); // Action handles navigation
}
</script>

<style scoped> /* Basic Styles */
.view-padding { padding: 2em; }
.input-container { max-width: 80%; margin: 2em auto; border: 1px solid #eee; border-radius: 8px; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
h2 { text-align: center; margin-bottom: 1.5em; }
.input-group { display: flex; gap: 10px; margin-bottom: 1em; }
.input-group input { flex-grow: 1; padding: 0.8em; border: 1px solid #ccc; border-radius: 4px; }
.input-group button { padding: 0.8em 1.5em; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
.input-group button:disabled { background-color: #cccccc; cursor: not-allowed; }
.error-text { color: red; font-size: 0.9em; }
.error-message { margin-top: 1em; color: #D8000C; background-color: #FFD2D2; border: 1px solid #D8000C; padding: 10px; border-radius: 4px; text-align: center; }
</style>