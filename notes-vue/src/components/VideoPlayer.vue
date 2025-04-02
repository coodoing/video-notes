<script setup>
import {ref, watch, onMounted} from 'vue';
import { defineProps, defineEmits, defineExpose } from 'vue';

const props = defineProps({
  src: {type: String, required: true}
});
const emit = defineEmits(['timeupdate']);

const videoRef = ref(null);

function handleTimeUpdate() {
  if (videoRef.value) {
    emit('timeupdate', videoRef.value.currentTime);
  }
}

// Expose seek function to parent component via template ref
function seek(time) {
  if (videoRef.value) {
    videoRef.value.currentTime = time;
    // Optional: auto-play after seeking
    // videoRef.value.play();
  }
}

defineExpose({seek});

// Watch for src changes to update the video element
watch(() => props.src, (newSrc) => {
  if (videoRef.value && newSrc) {
    videoRef.value.load(); // Reload the video source
  }
});

onMounted(() => {
  // Could add other event listeners here if needed (e.g., 'loadedmetadata')
})

</script>

<template>
  <div class="video-player">
    <video
        ref="videoRef"
        :src="props.src"
        controls
        @timeupdate="handleTimeUpdate"
        width="100%"
    >
      Your browser does not support the video tag.
    </video>
  </div>
</template>

<style scoped>
.video-player video {
  display: block; /* Prevents bottom space */
  max-width: 100%;
  background-color: #000; /* Black background for letterboxing */
}
</style>