// Use backend service name from docker-compose
export const API_BASE_URL = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '';

export const ENDPOINTS = {
  // Analytics endpoints
  MUSCLE_TRACKING: '/api/analytics/muscle-tracking',
  MUSCLE_VOLUME: '/api/analytics/muscle-volume',
  VOLUME_PROGRESSION: '/api/analytics/volume-progression',
  
  // Exercise endpoints
  ANALYZE_EXERCISE: '/api/exercise/analyze',
  ANALYZE_SENTIMENT: '/api/exercise/analyze/sentiment',
  
  // Chat endpoints
  CHAT: '/api/chat/',  
};
