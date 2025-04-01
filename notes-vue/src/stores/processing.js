// src/stores/processing.js
import { ref } from 'vue';
import { defineStore } from 'pinia';
import { useRouter } from 'vue-router';
import api from '@/services/api';

export const useProcessingStore = defineStore('processing', () => {
    const router = useRouter();

    // --- State ---
    const videoUrl = ref('');
    const videoId = ref(null);
    const transcriptId = ref(null);
    const rawTranscript = ref('');
    // MODIFIED: Default model and track selection/usage
    const selectedAiModel = ref('deepseek-coder'); // Default selection (e.g., gpt-4o)
    const generatedMarkdown = ref('');
    const modelUsed = ref(''); // Model confirmed by backend

    // Loading states
    const isLoadingDownload = ref(false);
    const isLoadingTranscribe = ref(false);
    const isLoadingGenerate = ref(false);

    // Completion flags
    const isDownloadComplete = ref(false);
    const isTranscribeComplete = ref(false);
    const isGenerateComplete = ref(false);

    const errorMessage = ref('');

    // --- Actions ---
    function resetState() {
        videoUrl.value = '';
        videoId.value = null;
        transcriptId.value = null;
        rawTranscript.value = '';
        // selectedAiModel.value = 'deepseek-coder'; // Keep last user selection on reset
        generatedMarkdown.value = '';
        modelUsed.value = ''; // Clear model used for previous result
        isLoadingDownload.value = false;
        isLoadingTranscribe.value = false;
        isLoadingGenerate.value = false;
        isDownloadComplete.value = false;
        isTranscribeComplete.value = false;
        isGenerateComplete.value = false;
        errorMessage.value = '';
        console.log('Processing store state reset.');
    }

    async function downloadVideo(url) {
        // ... (same as before) ...
        resetState();
        isLoadingDownload.value = true;
        errorMessage.value = '';
        videoUrl.value = url;
        try {
            await router.push({ name: 'DownloadPage' });
            const response = await api.downloadVideo(url);
            videoId.value = response.data.video_id;
            isDownloadComplete.value = true;
        } catch (error) {
            errorMessage.value = error.responseData?.detail || 'Failed to download video.';
        } finally {
            isLoadingDownload.value = false;
        }
    }

    async function transcribeVideo() {
        // ... (same as before) ...
        if (!videoId.value) return;
        isLoadingTranscribe.value = true;
        errorMessage.value = '';
        isTranscribeComplete.value = false;
        try {
            await router.push({ name: 'TranscribePage' });
            const response = await api.transcribeVideo(videoId.value);
            transcriptId.value = response.data.transcript_id;
            rawTranscript.value = response.data.transcript_text;
            isTranscribeComplete.value = true;
        } catch (error) {
            errorMessage.value = error.responseData?.detail || 'Failed to transcribe video.';
        } finally {
            isLoadingTranscribe.value = false;
        }
    }

    // MODIFIED generateMarkdownContent
    async function generateMarkdownContent(model) { // Takes model from component
        if (!transcriptId.value) {
            errorMessage.value = 'Cannot generate without a valid Transcript ID.';
            return;
        }
        if (!model) { // Ensure model is selected
            errorMessage.value = 'Please select an AI model before generating.';
            return;
        }
        isLoadingGenerate.value = true;
        errorMessage.value = '';
        selectedAiModel.value = model; // Update store state with the model being used NOW
        isGenerateComplete.value = false;
        generatedMarkdown.value = ''; // Clear previous markdown
        modelUsed.value = ''; // Clear previous model used


        try {
            // Navigate immediately if not already on Generate page
            if (router.currentRoute.value.name !== 'GeneratePage') {
                await router.push({ name: 'GeneratePage' });
                console.log('Navigated to Generate page.');
            }

            const response = await api.generateMarkdown(transcriptId.value, selectedAiModel.value); // Use the selected model
            generatedMarkdown.value = response.data.markdown_content;
            modelUsed.value = response.data.model_used; // Store the model confirmed by backend
            isGenerateComplete.value = true;
            console.log(`Markdown generation successful using ${modelUsed.value}.`);
        } catch(error) {
            console.error('Generation failed:', error);
            errorMessage.value = error.responseData?.detail || 'Failed to generate markdown.';
            // Stay on Generate page to show error
        } finally {
            isLoadingGenerate.value = false;
        }
    }

    return {
        // State
        videoUrl, videoId, transcriptId, rawTranscript,
        selectedAiModel, // Expose for v-model
        generatedMarkdown, modelUsed, // Expose for display
        isLoadingDownload, isLoadingTranscribe, isLoadingGenerate,
        isDownloadComplete, isTranscribeComplete, isGenerateComplete,
        errorMessage,
        // Actions
        downloadVideo, transcribeVideo, generateMarkdownContent, resetState,
    };
});