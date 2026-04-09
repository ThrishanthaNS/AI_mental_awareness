/**
 * API service - handles all HTTP requests to the backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * Send a message to the chatbot.
 */
export const sendMessage = async (message, sessionId = null) => {
  const response = await fetch(`${API_BASE_URL}/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  return response.json();
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
