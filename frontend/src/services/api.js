/**
 * API service - handles all HTTP requests to the backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * Send a message to the chatbot (text, audio, or video).
 */
export const sendMessage = async (message, mediaType = 'text', mediaData = null, sessionId = null) => {
  const url = `${API_BASE_URL}/chat/message`;

  if (mediaType === 'audio' || mediaType === 'video') {
    // For audio/video, use FormData
    const formData = new FormData();
    formData.append('message', message);
    formData.append('media_type', mediaType);
    formData.append('media', mediaData);
    if (sessionId) formData.append('session_id', sessionId);

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  } else {
    // For text, use JSON
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, media_type: mediaType, session_id: sessionId }),
    });
    return response.json();
  }
};

/**
 * Log a mood entry.
 */
export const logMood = async (mood, intensity, notes) => {
  const response = await fetch(`${API_BASE_URL}/mood/log`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mood, intensity, notes }),
  });
  return response.json();
};

/**
 * Get mood history.
 */
export const getMoodHistory = async () => {
  const response = await fetch(`${API_BASE_URL}/mood/history`);
  return response.json();
};

/**
 * Get recommendations.
 */
export const getRecommendations = async () => {
  const response = await fetch(`${API_BASE_URL}/recommendations/`);
  return response.json();
};

/**
 * Detect emotion from text.
 */
export const detectEmotion = async (text) => {
  const response = await fetch(`${API_BASE_URL}/detect/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  return response.json();
};
