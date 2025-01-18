import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useMuscleVolume } from '../useMuscleVolume';
import { fetchMuscleVolumeData } from '../../services/analytics';

// Mock the analytics service
jest.mock('../../services/analytics');
const mockFetchMuscleVolumeData = fetchMuscleVolumeData as jest.MockedFunction<typeof fetchMuscleVolumeData>;

const mockVolumeData = [
  {
    muscle_name: 'Chest',
    total_volume: 1000,
    date: '2025-01-15T00:00:00.000Z',
  },
  {
    muscle_name: 'Back',
    total_volume: 1500,
    date: '2025-01-15T00:00:00.000Z',
  },
];

describe('useMuscleVolume', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('fetches and returns muscle volume data', async () => {
    mockFetchMuscleVolumeData.mockResolvedValueOnce(mockVolumeData);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );

    const { result } = renderHook(() => useMuscleVolume('weekly'), { wrapper });

    // Initially loading
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeUndefined();

    // Wait for data to be loaded
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockVolumeData);
    expect(mockFetchMuscleVolumeData).toHaveBeenCalledWith('weekly');
  });

  it('handles error state', async () => {
    const error = new Error('Failed to fetch data');
    mockFetchMuscleVolumeData.mockRejectedValueOnce(error);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );

    const { result } = renderHook(() => useMuscleVolume('weekly'), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.data).toBeUndefined();
  });

  it('refetches data when timeframe changes', async () => {
    mockFetchMuscleVolumeData.mockResolvedValueOnce(mockVolumeData);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );

    const { result, rerender } = renderHook(
      (timeframe: 'weekly' | 'monthly') => useMuscleVolume(timeframe),
      { wrapper, initialProps: 'weekly' }
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Change timeframe to monthly
    mockFetchMuscleVolumeData.mockResolvedValueOnce([...mockVolumeData]);
    rerender('monthly');

    await waitFor(() => {
      expect(mockFetchMuscleVolumeData).toHaveBeenCalledWith('monthly');
    });
  });
});
