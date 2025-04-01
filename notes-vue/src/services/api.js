// src/services/api.js
import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

export default {
    downloadVideo(url) {
        return apiClient.post('api/v1/download', { url });
    },
    transcribeVideo(videoId) {
        return apiClient.post('api/v1/transcribe', { video_id: videoId });
    },
    generateMarkdown(transcriptId, modelType) {
        if (!modelType) {
            // Basic validation on frontend too
            return Promise.reject(new Error("Model type must be selected."));
        }
        return apiClient.post('api/v1/generate', { transcript_id: transcriptId, model_type: modelType });
    },
};

// Optional global error handler
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Call Error:', error.response || error.message);
        // Provide a default message if backend detail is missing
        const errorData = error.response?.data || {};
        errorData.detail = errorData.detail || error.message || 'An unknown API error occurred.';
        return Promise.reject({ ...error, responseData: errorData }); // Attach parsed detail
    }
);