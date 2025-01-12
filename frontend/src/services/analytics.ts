import { MuscleTrackingStatus } from '../types/exercise';
import { API_BASE_URL } from '../config';

export const fetchMuscleData = async (): Promise<MuscleTrackingStatus[]> => {
  const response = await fetch(`${API_BASE_URL}/analytics/muscle-tracking`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch muscle data');
  }

  return response.json();
};
