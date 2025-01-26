import { MuscleTrackingStatus, MuscleVolumeData, VolumeProgressionData, VolumeProgressionResponse } from '../types/exercise';
import { API_BASE_URL, ENDPOINTS } from '../config';

export const fetchMuscleData = async (): Promise<MuscleTrackingStatus[]> => {
  // TODO: Get actual user ID from auth context. Using 1 for now.
  const userId = 1;
  const response = await fetch(`${ENDPOINTS.MUSCLE_TRACKING}?user_id=${userId}`, {
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

export const fetchMuscleVolumeData = async (timeframe: 'weekly' | 'monthly'): Promise<MuscleVolumeData[]> => {
  // TODO: Get actual user ID from auth context. Using 1 for now.
  const userId = 1;
  const response = await fetch(`${ENDPOINTS.MUSCLE_VOLUME}?timeframe=${timeframe}&user_id=${userId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch muscle volume data');
  }

  return response.json();
};

export const fetchVolumeProgressionData = async (timeframe: 'weekly' | 'monthly'): Promise<VolumeProgressionData[]> => {
  // TODO: Get actual user ID from auth context. Using 1 for now.
  const userId = 1;
  const response = await fetch(`${ENDPOINTS.VOLUME_PROGRESSION}?timeframe=${timeframe}&user_id=${userId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch volume progression data');
  }

  const data: VolumeProgressionResponse = await response.json();
  
  // Transform the data into the expected format
  const transformedData: VolumeProgressionData[] = Object.entries(data).flatMap(([muscleName, dataPoints]) =>
    dataPoints.map(point => ({
      muscle_name: muscleName,
      date: point.date,
      total_volume: point.volume,
    }))
  );

  return transformedData;
};
