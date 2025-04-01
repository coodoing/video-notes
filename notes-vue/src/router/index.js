import { createRouter, createWebHistory } from "vue-router";
// import Vue from "vue";
// import Router from "vue-router";
// Vue.use(Router); //main.js

import HelloWorld from "@/components/HelloWorld.vue";
// import SearchPage from "@/components/SearchPage.vue";
// import DisplayPage from "@/components/DisplayPage.vue";
// import MarkdownitPage from "@/components/MarkdownitPage.vue";
// import VideoSearchProcessor from "@/components/workflow/OnePageVideoSearchProcessor.vue";
// import InputVideo from "@/components/workflow/InputVideo.vue";
// import DownloadVideo from "@/components/workflow/DownloadVideo.vue";
// import TranscribeVideo from "@/components/workflow/TranscribeVideo.vue";
// import GenerateMarkdown from "@/components/workflow/GenerateMarkdown.vue";
import InputPage from '@/views/InputPage.vue';
import DownloadPage from '@/views/DownloadPage.vue';
import TranscribePage from '@/views/TranscribePage.vue';
import GeneratePage from '@/views/GeneratePage.vue';
import PolishPage from '@/views/PolishPage.vue';

import { useProcessingStore } from '@/stores/processing'; // Import store

const routes = [
  { path: '/:pathMatch(.*)*', redirect: '/' }, // Catch all redirect home
  {
    path: "/",
    name: "HelloWorld",
    component: HelloWorld,
  },
  // {
  //   path: "/mdp",
  //   name: "MarkdownitPage",
  //   component: MarkdownitPage,
  // },
  // {
  //   path: "/search",
  //   name: "SearchPage",
  //   component: SearchPage,
  // },
  // {
  //   path: "/display",
  //   name: "DisplayPage",
  //   component: DisplayPage,
  // },
  // {
  //   path: "/workflow/vsp",
  //   name: "VideoSearchProcessor",
  //   component: VideoSearchProcessor,
  // },
  // {
  //   path: "/workflow/input",
  //   name: "Input",
  //   component: InputVideo,
  // },
  // {
  //   path: "/workflow/download/:encodedUrl",
  //   name: "Download",
  //   component: DownloadVideo,
  //   props: true, // Pass route params as props to the component
  // },
  // {
  //   path: "/workflow/transcribe",
  //   name: "Transcribe",
  //   component: TranscribeVideo,
  // },
  // {
  //   path: "/workflow/generate",
  //   name: "Generate",
  //   component: GenerateMarkdown,
  // },
  {
    path: '/api/input',
    name: 'InputPage',
    component: InputPage
  },
  {
    path: '/api/download', // No need for ID in URL if store holds it
    name: 'DownloadPage',
    component: DownloadPage,
    meta: { requiresDownloadAttempt: true } // Requires download to have been started
  },
  {
    path: '/api/transcribe',
    name: 'TranscribePage',
    component: TranscribePage,
    meta: { requiresDownloadComplete: true } // Requires download to be finished
  },
  {
    path: '/api/generate',
    name: 'GeneratePage',
    component: GeneratePage,
    meta: { requiresTranscribeComplete: true } // Requires transcribe to be finished
  },
  {
    path: '/api/polish',
    name: 'PolishPage',
    component: PolishPage,
    meta: { requiresGenerateComplete: true } // Requires generate to be finished
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

//--- Navigation Guard ---
router.beforeEach((to, from, next) => {
  const store = useProcessingStore(); // Get store instance outside condition

  // Always allow navigation to Input page, reset state if coming from others
  if (to.name === 'InputPage') {
    if (from.name && from.name !== 'InputPagePage') {
      console.log("Navigating to InputPage, resetting state.");
      store.resetState();
    }
    return next();
  }

  // Check requirements for specific routes
  if (to.meta.requiresDownloadAttempt && !store.videoUrl) {
    // Must have at least attempted download (i.e., started the process)
    console.warn("Guard: Accessing Download page without starting.");
    return next({ name: 'InputPage' });
  }
  if (to.meta.requiresDownloadComplete && !store.isDownloadComplete) {
    console.warn("Guard: Download not complete. Redirecting.");
    // Redirect to Download page if started, else Input
    return next(store.videoUrl ? { name: 'DownloadPage' } : { name: 'InputPage' });
  }
  if (to.meta.requiresTranscribeComplete && !store.isTranscribeComplete) {
    console.warn("Guard: Transcription not complete. Redirecting.");
    return next(store.isDownloadComplete ? { name: 'TranscribePage' } : { name: 'DownloadPage' });
  }
  if (to.meta.requiresGenerateComplete && !store.isGenerateComplete) {
    console.warn("Guard: Generation not complete. Redirecting.");
    return next(store.isTranscribeComplete ? { name: 'GeneratePage' } : { name: 'TranscribePage' });
  }

  // If all checks pass
  next();
});

export default router;
