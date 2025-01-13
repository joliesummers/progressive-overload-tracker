import { MuscleTrackingStatus } from '../types/exercise';
import { API_BASE_URL, ENDPOINTS } from '../config';

export const fetchMuscleData = async (): Promise<MuscleTrackingStatus[]> => {
  const response = await fetch(ENDPOINTS.MUSCLE_TRACKING, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch muscle data');
  }

  return response.json();
};
