<template>
  <div class="polish-container view-padding">
    <h2>5. 内容润色与主题</h2>
    <p class="info">应用不同的 CSS 主题来预览最终输出。</p>

    <div class="controls">
      <label for="theme-select">选择主题:</label>
      <select id="theme-select" v-model="selectedTheme">
        <option value="default">默认</option>
        <option value="github-light">GitHub Light</option>
        <option value="academic">Academic</option>
        <option value="dark-mode">Dark Mode</option>
      </select>
    </div>

    <div v-if="store.generatedMarkdown" class="markdown-preview-area">
      <!-- Apply selected theme class -->
      <div :class="['theme-container', selectedTheme]" v-html="renderedMarkdown"></div>
    </div>
    <div v-else class="error-message">
      没有可供润色的 Markdown 内容。
      <router-link :to="{ name: 'GeneratePage' }">返回生成页面</router-link>
    </div>

    <div class="action-buttons">
      <button @click="goBackToGenerate">返回编辑</button>
      <button @click="goBackHome">完成 / 返回首页</button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useProcessingStore } from '@/stores/processing';
import { marked } from 'marked';
import { useRouter } from 'vue-router';

const store = useProcessingStore();
const router = useRouter();
const selectedTheme = ref('default'); // Default theme class

const renderedMarkdown = computed(() => {
  if (store.generatedMarkdown) {
    return marked.parse(store.generatedMarkdown);
  }
  return '<p><em>无内容可渲染...</em></p>';
});

function goBackToGenerate() {
  router.push({ name: 'GeneratePage' }); // Go back to potentially regenerate
}

function goBackHome() {
  store.resetState(); // Final step, reset state
  router.push({ name: 'InputPage' });
}

// Ensure state is valid on mount
onMounted(() => {
  if (!store.generatedMarkdown || !store.isGenerateComplete) {
    console.warn("PolishPage mounted without generation completion. Redirecting.");
    router.replace(store.isTranscribeComplete ? { name: 'GeneratePage' } : { name: 'TranscribePage' });
  }
});
</script>

<style scoped>
.view-padding { padding: 2em; }
.polish-container { max-width: 80%; margin: 2em auto; }
h2 { text-align: center; margin-bottom: 0.5em; }
.info { text-align: center; color: #666; margin-bottom: 1.5em; }
.controls { text-align: center; margin-bottom: 2em; }
.controls label { margin-right: 10px; }
.controls select { padding: 8px 12px; border-radius: 4px; border: 1px solid #ccc; min-width: 200px; }
.markdown-preview-area { margin-top: 1em; }
.theme-container {
  border: 1px solid #ddd;
  padding: 2em;
  border-radius: 8px;
  background-color: #fff; /* Default background */
  color: #333; /* Default text */
  line-height: 1.6;
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Base Markdown styles (applied via :deep selector to v-html content) */
.theme-container :deep(h1),
.theme-container :deep(h2),
.theme-container :deep(h3),
.theme-container :deep(h4) {
  margin-top: 1.5em;
  margin-bottom: 0.8em;
  line-height: 1.3;
  font-weight: 600;
}
.theme-container :deep(h1) { font-size: 2em; border-bottom: 1px solid #eee; padding-bottom: 0.3em;}
.theme-container :deep(h2) { font-size: 1.6em; border-bottom: 1px solid #eee; padding-bottom: 0.3em;}
.theme-container :deep(h3) { font-size: 1.3em; }
.theme-container :deep(p) { margin-bottom: 1em; }
.theme-container :deep(ul),
.theme-container :deep(ol) { margin-left: 2em; margin-bottom: 1em; padding-left: 1em; }
.theme-container :deep(li) { margin-bottom: 0.4em; }
.theme-container :deep(code) {
  font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
  background-color: rgba(27,31,35,.05);
  padding: .2em .4em;
  margin: 0;
  font-size: 85%;
  border-radius: 3px;
}
.theme-container :deep(pre) {
  font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 3px;
  margin-bottom: 1em;
}
.theme-container :deep(pre code) {
  display: inline;
  padding: 0;
  margin: 0;
  overflow: visible;
  line-height: inherit;
  word-wrap: normal;
  background-color: transparent;
  border: 0;
}
.theme-container :deep(blockquote) {
  margin: 1em 0;
  padding: 0 1em;
  color: #6a737d;
  border-left: .25em solid #dfe2e5;
}
.theme-container :deep(strong) { font-weight: 600; }
.theme-container :deep(em) { font-style: italic; }
.theme-container :deep(a) { color: #0366d6; text-decoration: none; }
.theme-container :deep(a:hover) { text-decoration: underline; }

/* --- Theme Specific Styles --- */

/* Default Theme (already styled above mostly) */
.theme-container.default {
  /* Add any specific overrides if needed */
}

/* GitHub Light Theme (Simplified) */
.theme-container.github-light {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
  color: #24292e;
  background-color: #fff;
}
.theme-container.github-light :deep(h1),
.theme-container.github-light :deep(h2) {
  border-bottom-color: #eaecef;
}
/* Add more github specific styles if desired */

/* Academic Theme (Simple Example) */
.theme-container.academic {
  font-family: 'Georgia', serif;
  line-height: 1.7;
  background-color: #fdfdfd;
  border-left: 5px solid #4a90e2;
}
.theme-container.academic :deep(h1),
.theme-container.academic :deep(h2),
.theme-container.academic :deep(h3) {
  color: #333;
  border-bottom: none;
  font-weight: normal;
}
.theme-container.academic :deep(p) { text-align: justify; }

/* Dark Mode Theme (Simple Example) */
.theme-container.dark-mode {
  background-color: #2d2d2d;
  color: #ccc;
  border-color: #444;
}
.theme-container.dark-mode :deep(h1),
.theme-container.dark-mode :deep(h2) {
  border-bottom-color: #444;
  color: #eee;
}
.theme-container.dark-mode :deep(code) { background-color: #444; color: #eee;}
.theme-container.dark-mode :deep(pre) { background-color: #333; }
.theme-container.dark-mode :deep(blockquote) { color: #999; border-left-color: #555; }
.theme-container.dark-mode :deep(a) { color: #68a0f0; }


.error-message { margin-top: 1em; color: #D8000C; background-color: #FFD2D2; border: 1px solid #D8000C; padding: 15px; border-radius: 4px; text-align: center; }
.error-message a { margin-left: 10px; }
.action-buttons { margin-top: 2em; text-align: center; display: flex; justify-content: center; gap: 15px; }
button { padding: 0.8em 1.5em; border: none; border-radius: 4px; cursor: pointer; }
.action-buttons button:first-of-type { background-color: #6c757d; color: white;} /* Back button */
.action-buttons button:last-of-type { background-color: #17a2b8; color: white;} /* Finish button */

</style>