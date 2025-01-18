import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useVolumeProgression } from '../useVolumeProgression';
import { fetchVolumeProgressionData } from '../../services/analytics';

// Mock the analytics service
jest.mock('../../services/analytics', () => ({
  fetchVolumeProgressionData: jest.fn(),
}));

const mockFetchVolumeProgressionData = fetchVolumeProgressionData as jest.MockedFunction<typeof fetchVolumeProgressionData>;

describe('useVolumeProgression', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
  });

  it('fetches volume progression data successfully', async () => {
    const mockData = [
      {
        date: '2025-01-16',
        total_volume: 3000,
        chest_volume: 800,
        back_volume: 900,
        legs_volume: 1300,
      },
    ];

    mockFetchVolumeProgressionData.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useVolumeProgression('weekly'), {
      wrapper,
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(mockFetchVolumeProgressionData).toHaveBeenCalledWith('weekly');
  });

  it('handles error state', async () => {
    const error = new Error('Failed to fetch data');
    mockFetchVolumeProgressionData.mockRejectedValueOnce(error);

    const { result } = renderHook(() => useVolumeProgression('weekly'), {
      wrapper,
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBeDefined();
  });

  it('refetches data when timeframe changes', async () => {
    const mockData = [
      {
        date: '2025-01-16',
        total_volume: 3000,
        chest_volume: 800,
        back_volume: 900,
        legs_volume: 1300,
      },
    ];

    mockFetchVolumeProgressionData.mockResolvedValue(mockData);

    const { result, rerender } = renderHook(
      ({ timeframe }) => useVolumeProgression(timeframe),
      {
        wrapper,
        initialProps: { timeframe: 'weekly' },
      }
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(mockFetchVolumeProgressionData).toHaveBeenCalledWith('weekly');

    // Change timeframe to monthly
    rerender({ timeframe: 'monthly' });

    await waitFor(() => {
      expect(mockFetchVolumeProgressionData).toHaveBeenCalledWith('monthly');
    });
  });
});
