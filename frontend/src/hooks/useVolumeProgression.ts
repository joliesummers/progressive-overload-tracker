import { useQuery } from '@tanstack/react-query';
import { fetchVolumeProgressionData } from '../services/analytics';
import { VolumeProgressionData } from '../types/exercise';

export const useVolumeProgression = (timeframe: 'weekly' | 'monthly'): { data: VolumeProgressionData[] | undefined, isLoading: boolean } => {
  return useQuery({
    queryKey: ['volumeProgression', timeframe],
    queryFn: () => fetchVolumeProgressionData(timeframe),
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
};
