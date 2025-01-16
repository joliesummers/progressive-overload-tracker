import { useQuery } from '@tanstack/react-query';
import { fetchMuscleVolumeData } from '../services/analytics';

export const useMuscleVolume = (timeframe: 'weekly' | 'monthly') => {
  return useQuery({
    queryKey: ['muscleVolume', timeframe],
    queryFn: () => fetchMuscleVolumeData(timeframe),
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
};
