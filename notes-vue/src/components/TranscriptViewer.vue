<script setup>
import {computed, ref, watch} from 'vue';
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  transcript: {type: Array, default: () => []},
  currentTime: {type: Number, default: 0},
  interactive: {type: Boolean, default: false} // Allow clicking to seek
});
const emit = defineEmits(['seek']);

const transcriptContainerRef = ref(null);
const activeSegmentRef = ref(null); // Ref for the currently active segment element

const activeSegmentIndex = computed(() => {
  return props.transcript.findIndex(segment =>
      props.currentTime >= segment.start && props.currentTime < segment.end
  );
});

function formatTime(seconds) {
  const date = new Date(0);
  date.setSeconds(seconds);
  return date.toISOString().substr(14, 5); // MM:SS format
}

function handleSegmentClick(startTime) {
  if (props.interactive) {
    emit('seek', startTime);
  }
}

// Scroll the active segment into view
watch(activeSegmentIndex, (newIndex, oldIndex) => {
  if (newIndex !== -1 && newIndex !== oldIndex && activeSegmentRef.value && transcriptContainerRef.value) {
    // Use scrollIntoView with options for smooth behavior and centering
    activeSegmentRef.value.scrollIntoView({
      behavior: 'smooth', // 'auto' or 'smooth'
      block: 'center',     // 'start', 'center', 'end', or 'nearest'
      inline: 'nearest'
    });
  }
});

</script>

<template>
  <div ref="transcriptContainerRef" class="transcript-viewer">
    <div
        v-for="(segment, index) in transcript"
        :key="index"
        :ref="el => { if (index === activeSegmentIndex) activeSegmentRef = el }"
        class="transcript-segment"
        :class="{ active: index === activeSegmentIndex, interactive: props.interactive }"
        @click="handleSegmentClick(segment.start)"
    >
      <span class="timestamp">[{{ formatTime(segment.start) }}]</span>
      {{ segment.text }}
    </div>
    <div v-if="!transcript || transcript.length === 0">
      No transcript available.
    </div>
  </div>
</template>

<style scoped>
.transcript-viewer {
  font-size: 0.9em;
  line-height: 1.6;
  color: #333;
}

.transcript-segment {
  padding: 5px 8px;
  margin-bottom: 4px;
  border-radius: 4px;
  transition: background-color 0.2s ease-in-out;
}

.transcript-segment.interactive {
  cursor: pointer;
}

.transcript-segment.interactive:hover {
  background-color: #e9ecef; /* Light hover effect */
}

.transcript-segment.active {
  background-color: #d1e7ff; /* Bootstrap's info light background */
  font-weight: bold;
}

.timestamp {
  font-weight: bold;
  color: #0056b3; /* Darker blue */
  margin-right: 8px;
  font-size: 0.9em;
}
</style>