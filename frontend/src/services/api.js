/**
 * API service - handles all HTTP requests to the backend.
 */

const DEFAULT_BASES = [
  import.meta.env.VITE_API_URL,
  'http://127.0.0.1:8000/api/v1',
  'http://localhost:8000/api/v1',
  'http://127.0.0.1:8001/api/v1',
  'http://localhost:8001/api/v1',
].filter(Boolean);

const API_BASE_URL = DEFAULT_BASES[0];

const tryApiBases = async (requestFn) => {
  let lastError = null;

  for (const base of DEFAULT_BASES) {
    try {
      return await requestFn(base);
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError || new Error('All API base URLs failed');
};

const parseResponse = async (response) => {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data?.detail || data?.error || `HTTP ${response.status}`;
    throw new Error(message);
  }
  return data;
};

/**
 * Send a message to the chatbot (text, audio, or video).
 */
export const sendMessage = async (message, mediaType = 'text', mediaData = null, sessionId = null) => {
  return tryApiBases(async (base) => {
    const url = `${base}/chat/message`;

  if (mediaType === 'audio' || mediaType === 'video') {
    // For audio/video, use FormData
    const formData = new FormData();
    formData.append('message', message);
    formData.append('media_type', mediaType);
    if (mediaData) {
      if (mediaType === 'audio') {
        const audioExt = mediaData.type.includes('webm') ? 'webm' : mediaData.type.includes('wav') ? 'wav' : 'ogg';
        formData.append('media', mediaData, `voice.${audioExt}`);
      } else {
        const videoExt = mediaData.type.includes('png') ? 'png' : mediaData.type.includes('jpeg') ? 'jpg' : 'webm';
        formData.append('media', mediaData, `capture.${videoExt}`);
      }
    }
    if (sessionId) formData.append('session_id', sessionId);

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });
      return parseResponse(response);
    }

    // For text, use JSON
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, media_type: mediaType, session_id: sessionId }),
    });
    return parseResponse(response);
  });
};

/**
 * Log a mood entry.
 */
export const logMood = async (mood, intensity, notes) => {
  return tryApiBases(async (base) => {
    const response = await fetch(`${base}/mood/log`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mood, intensity, notes }),
    });
    return parseResponse(response);
  });
};

/**
 * Get mood history.
 */
export const getMoodHistory = async () => {
  return tryApiBases(async (base) => {
    const response = await fetch(`${base}/mood/history`);
    return parseResponse(response);
  });
};

/**
 * Get recommendations.
 */
export const getRecommendations = async () => {
  return tryApiBases(async (base) => {
    const response = await fetch(`${base}/recommendations/`);
    return parseResponse(response);
  });
};

/**
 * Detect emotion from text.
 */
export const detectEmotion = async (text) => {
  return tryApiBases(async (base) => {
    const response = await fetch(`${base}/detect/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    return parseResponse(response);
  });
};

/**
 * Get all chat sessions for a user.
 */
export const getChatSessions = async (userId = 1) => {
  return tryApiBases(async (base) => {
    const response = await fetch(`${base}/chat/sessions?user_id=${encodeURIComponent(userId)}`);
    return parseResponse(response);
  });
};

/**
 * Get chat history for one session.
 */
export const getChatHistory = async (sessionId) => {
  return tryApiBases(async (base) => {
    const response = await fetch(`${base}/chat/history?session_id=${encodeURIComponent(sessionId)}`);
    return parseResponse(response);
  });
};

/**
 * Get dashboard insights derived from chat history.
 */
export const getChatInsights = async (userId = 1) => {
  return tryApiBases(async (base) => {
    const response = await fetch(`${base}/chat/insights?user_id=${encodeURIComponent(userId)}`);
    return parseResponse(response);
  });
};
