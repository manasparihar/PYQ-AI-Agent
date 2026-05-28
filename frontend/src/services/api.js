import axios from 'axios';

// 1. Centralized API Configuration
// Replace all hardcoded localhost API URLs with environment-based configuration.
export const API_URL = import.meta.env.VITE_API_URL || '';

// 2. Fallback console warning if env variable missing
if (!API_URL) {
  console.warn("WARNING: VITE_API_URL is missing! Please set it in your environment variables. API calls will likely fail.");
}

// 3. Configure Axios properly
export const api = axios.create({
  baseURL: API_URL,
  timeout: 60000, // 60 seconds timeout
});

// 4. Add proper error handling for: backend unavailable, network errors, timeout errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        console.error("API Error: Timeout. The backend took too long to respond.");
      } else {
        console.error("API Error: Network Error or Backend Unavailable. Please verify the Render backend is live.");
      }
    } else {
      console.error(`API Error [${error.response.status}]:`, error.response.data);
    }
    return Promise.reject(error);
  }
);

// --- Session APIs ---
export const createSession = async () => {
  const response = await api.post('/conversation/create-session');
  return response.data;
};

export const getSessionHistory = async (sessionId) => {
  const response = await api.get(`/conversation/session/${sessionId}`);
  return response.data;
};

// --- Chat APIs ---
export const chatWithAI = async (sessionId, prompt) => {
  const response = await api.post(`/conversation/chat/${sessionId}`, { prompt });
  return response.data;
};

/**
 * Streams the AI response chunk by chunk using native fetch.
 * Uses VITE_API_URL to construct the correct backend endpoint.
 */
export const streamChatWithAI = async (sessionId, prompt, onChunk) => {
  try {
    const response = await fetch(`${API_URL}/conversation/chat-stream/${sessionId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => null);
      throw new Error(errData?.detail || `HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      if (chunk) {
        onChunk(chunk);
      }
    }
    
    return { success: true };
  } catch (error) {
    console.error("Streaming error: Network error or backend unavailable", error);
    throw error;
  }
};

// --- PDF APIs (legacy, recommend moving fully to pdfService.js) ---
export const generatePDF = async (sessionId, downloadOnlyLatest = false) => {
  const response = await api.post(`/generate-pdf/${sessionId}?download_only_latest=${downloadOnlyLatest}`);
  return response.data;
};

export const getPdfDownloadUrl = (pdfPath) => {
  const path = pdfPath.replace(/\\/g, '/');
  return `${API_URL}/${path}`;
};
