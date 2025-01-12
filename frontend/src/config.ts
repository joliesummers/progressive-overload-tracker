export const API_BASE_URL = 'http://localhost:8000';

export const ENDPOINTS = {
  // Auth endpoints
  LOGIN: '/auth/token',
  REGISTER: '/auth/register',
  GET_USER: '/auth/me',
  RESET_PASSWORD: '/auth/reset-password',
  
  // Analytics endpoints
  MUSCLE_TRACKING: '/analytics/muscle-tracking',
  
  // Exercise endpoints
  ANALYZE_EXERCISE: '/exercise/analyze',
  ANALYZE_SENTIMENT: '/exercise/analyze/sentiment',
};
