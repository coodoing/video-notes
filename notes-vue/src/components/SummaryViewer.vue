<script setup>
import { defineProps } from 'vue';

defineProps({
  summary: {type: String, default: ''}
});
</script>

<template>
  <div class="summary-viewer">
    <p v-if="summary">{{ summary }}</p>
    <p v-else>Summary not available.</p>
  </div>
</template>

<style scoped>
.summary-viewer {
  line-height: 1.6;
  white-space: pre-wrap; /* Respect newlines in the summary */
  color: #333;
}
</style>