<template>
  <div class="step-container view-padding">
    <h2>4. 生成 Markdown</h2>
    <p class="info">处理 Transcript ID: {{ store.transcriptId || 'N/A' }}</p>

    <!-- Model Selection (Always visible if transcript exists, enable/disable based on state) -->
    <div class="controls-section" v-if="store.isTranscribeComplete">
      <div class="model-selection">
        <label for="model-select">选择 AI 模型:</label>
        <!-- Bind select directly to store state -->
        <select id="model-select" v-model="store.selectedAiModel" :disabled="store.isLoadingGenerate">
          <option value="deepseek-coder">DeepSeek coder </option>
          <option value="gpt-4o">GPT-4o </option>
          <option value="claude-3-opus">Claude 3 Opus </option>
          <option value="glm-4v">GLM-4V </option>
          <option value="other-model">其他 </option>
        </select>
      </div>
      <div class="action-buttons main-actions">
        <!-- Generate / Regenerate Button -->
        <button @click="triggerGeneration" :disabled="store.isLoadingGenerate || !store.isTranscribeComplete">
                <span v-if="store.isLoadingGenerate">
                   <span class="spinner">⚙️</span> 生成中...
                </span>
          <span v-else-if="store.isGenerateComplete">重新生成</span>
          <span v-else>开始生成</span>
        </button>
        <!-- Polish Button (only if generation complete) -->
        <button v-if="store.isGenerateComplete && !store.errorMessage" @click="goToPolishPage">
          润色和主题
        </button>
      </div>
    </div>


    <!-- Loading Indicator -->
    <div v-if="store.isLoadingGenerate" class="status-indicator loading">
      <span class="spinner">⚙️</span> 正在生成内容... (使用模型: {{ store.selectedAiModel }})
    </div>

    <!-- Error Display -->
    <div v-if="store.errorMessage" class="error-message"> <!-- Show error anytime it exists -->
      处理失败：{{ store.errorMessage }}
      <div class="action-buttons error-actions">
        <!-- Retry only possible if transcription is complete -->
        <button @click="triggerGeneration" v-if="store.isTranscribeComplete" :disabled="store.isLoadingGenerate">重试生成</button>
        <button @click="goBackHome">返回首页</button>
      </div>
    </div>

    <!-- Result Display (only if generation is complete and no error occurred *during* generation) -->
    <div v-if="store.isGenerateComplete && !store.errorMessage" class="generation-result">
      <h3>✅ 生成完成 (使用模型: {{ store.modelUsed }})</h3>
      <div class="markdown-render-area" v-html="renderedMarkdown"></div>
      <!-- Polish button is now in the controls section above -->
    </div>

    <!-- markdown Preview -->
    <details class="transcript-preview" v-if="store.generatedMarkdown">
      <summary>显示/隐藏markdown原内容</summary>
      <pre>{{ store.generatedMarkdown }}</pre>
    </details>
    <!-- Transcript Preview -->
    <details class="transcript-preview" v-if="store.rawTranscript">
      <summary>显示/隐藏原始字幕</summary>
      <pre>{{ store.rawTranscript }}</pre>
    </details>

  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'; // Removed watch as v-model handles sync
import { useProcessingStore } from '@/stores/processing';
import { useRouter } from 'vue-router';
import { marked } from 'marked';

const store = useProcessingStore();
const router = useRouter();

// Render markdown from store
const renderedMarkdown = computed(() => {
  if (store.generatedMarkdown) {
    return marked.parse(store.generatedMarkdown);
  }
  return '';
});

// Trigger generation using the currently selected model in the store
function triggerGeneration() {
  if (store.isTranscribeComplete) {
    // Clear previous error message before trying again
    store.errorMessage = '';
    store.generateMarkdownContent(store.selectedAiModel);
  } else {
    console.error("Cannot generate, transcription not complete.");
    store.errorMessage = "无法生成：字幕解析未完成。";
  }
}

function goToPolishPage() {
  if (store.isGenerateComplete) {
    router.push({ name: 'PolishPage' });
  }
}

function goBackHome() {
  store.resetState();
  router.push({ name: 'InputPage' });
}

// Ensure state is valid on mount
onMounted(() => {
  if (!store.transcriptId || !store.isTranscribeComplete) {
    console.warn("GeneratePage mounted without transcription completion. Redirecting.");
    router.replace(store.isDownloadComplete ? { name: 'TranscribePage' } : { name: 'DownloadPage' });
  }
  // No automatic generation on mount, user must click button.
});

</script>

<style scoped> /* Reuse and adapt previous styles */
.view-padding { padding: 2em; }
.step-container { max-width: 80%; margin: 2em auto; border: 1px solid #eee; border-radius: 8px; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
h2 { margin-bottom: 0.5em; text-align: center;}
.info { color: #666; margin-bottom: 1.5em; text-align: center;}
.controls-section { /* Group model select and main actions */
  padding: 1.5em;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eee;
  margin-bottom: 2em;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5em;
}
.model-selection { display: flex; align-items: center; gap: 10px; }
.model-selection label { font-weight: 500; }
.model-selection select { padding: 8px 12px; border-radius: 4px; border: 1px solid #ccc; min-width: 200px;}
.status-indicator { padding: 1.5em; border-radius: 6px; margin: 1em auto; font-size: 1.1em; display: flex; align-items: center; justify-content: center; gap: 10px; text-align: center; width: fit-content; }
.loading { background-color: #fff3e0; border: 1px solid #ffe0b2; color: #e65100; }
.error-message { margin: 1.5em 2em; color: #D8000C; background-color: #FFD2D2; border: 1px solid #D8000C; padding: 15px; border-radius: 4px; text-align: center; }
.generation-result { margin-top: 1.5em; padding: 0 2em 2em 2em; /* Padding around result */ }
.generation-result h3 { text-align: center; color: #28a745; margin-bottom: 1em; }
.markdown-render-area { background-color: #f9f9f9; border: 1px solid #e0e0e0; padding: 1.5em; border-radius: 4px; margin-bottom: 1.5em; line-height: 1.6; }
/* Base Markdown styles (same as before) */
.markdown-render-area :deep(h1), .markdown-render-area :deep(h2), .markdown-render-area :deep(h3) { margin-top: 1em; margin-bottom: 0.5em; line-height: 1.3; }
.markdown-render-area :deep(p) { margin-bottom: 1em; }
.markdown-render-area :deep(ul), .markdown-render-area :deep(ol) { margin-left: 2em; margin-bottom: 1em; }
.markdown-render-area :deep(code) { background-color: #eee; padding: 0.2em 0.4em; border-radius: 3px; }
.markdown-render-area :deep(pre code) { display: block; padding: 1em; background-color: #eef; overflow-x: auto; }
.action-buttons { margin-top: 1em; display: flex; justify-content: center; gap: 15px; }
button { padding: 0.8em 1.5em; border: none; border-radius: 4px; cursor: pointer; font-size: 0.95em;}
button:disabled { background-color: #cccccc; cursor: not-allowed; opacity: 0.7;}
.main-actions button:first-of-type { background-color: #007bff; color: white; } /* Generate/Regenerate */
.main-actions button:last-of-type { background-color: #28a745; color: white;} /* Polish */
.error-actions button:first-of-type { background-color: #ffc107; color: #333; } /* Retry */
.error-actions button:last-of-type { background-color: #6c757d; color: white; } /* Home */
.transcript-preview { margin: 2em; padding-top: 1em; border-top: 1px dashed #ccc;}
.transcript-preview summary { cursor: pointer; color: #007bff; margin-bottom: 0.5em;}
.transcript-preview pre { background-color: #f0f0f0; border: 1px solid #ddd; padding: 10px; border-radius: 4px; max-height: 150px; overflow-y: auto; font-size: 0.85em; white-space: pre-wrap; word-wrap: break-word;}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.spinner { display: inline-block; animation: spin 1.5s linear infinite; font-size: 1.1em; vertical-align: middle; }
</style>