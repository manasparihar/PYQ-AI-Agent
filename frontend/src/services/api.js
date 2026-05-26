import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
});

export const createSession = async () => {
  const response = await api.post('/conversation/create-session');
  return response.data;
};

export const chatWithAI = async (sessionId, prompt) => {
  const response = await api.post(`/conversation/chat/${sessionId}`, { prompt });
  return response.data;
};

export const getSessionHistory = async (sessionId) => {
  const response = await api.get(`/conversation/session/${sessionId}`);
  return response.data;
};

export const generatePDF = async (sessionId, downloadOnlyLatest = false) => {
  const response = await api.post(`/generate-pdf/${sessionId}?download_only_latest=${downloadOnlyLatest}`);
  return response.data;
};

export const getPdfDownloadUrl = (pdfPath) => {
  // Replace Windows backslashes with forward slashes for the URL
  const path = pdfPath.replace(/\\/g, '/');
  return `${API_URL}/${path}`;
};

/**
 * Streams the AI response chunk by chunk using native fetch.
 * @param {string} sessionId 
 * @param {string} prompt 
 * @param {function} onChunk - Callback fired when a new chunk of text arrives
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
      // Try to parse error from backend if possible
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
    console.error("Streaming error:", error);
    throw error;
  }
};
