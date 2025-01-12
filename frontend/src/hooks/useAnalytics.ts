import { useQuery } from '@tanstack/react-query';
import { fetchMuscleData } from '../services/analytics';

export const useAnalytics = () => {
  return useQuery({
    queryKey: ['muscleData'],
    queryFn: fetchMuscleData,
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
};
