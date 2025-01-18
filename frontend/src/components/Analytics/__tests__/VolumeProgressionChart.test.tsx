import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import VolumeProgressionChart from '../VolumeProgressionChart';

const theme = createTheme();

describe('VolumeProgressionChart', () => {
  const mockData = [
    {
      date: '2025-01-16',
      total_volume: 3000,
      chest_volume: 800,
      back_volume: 900,
      legs_volume: 1300,
    },
    {
      date: '2025-01-15',
      total_volume: 2800,
      chest_volume: 750,
      back_volume: 850,
      legs_volume: 1200,
    },
  ];

  const renderChart = (props: any) => {
    return render(
      <ThemeProvider theme={theme}>
        <VolumeProgressionChart {...props} />
      </ThemeProvider>
    );
  };

  it('renders without crashing', () => {
    renderChart({ volumeData: mockData, timeframe: 'weekly' });
    expect(screen.getByText(/Volume Progression/)).toBeInTheDocument();
  });

  it('displays "No volume progression data available" when data is empty', () => {
    renderChart({ volumeData: [], timeframe: 'weekly' });
    expect(screen.getByText(/No volume progression data available/)).toBeInTheDocument();
  });

  it('shows correct timeframe in title', () => {
    renderChart({ volumeData: mockData, timeframe: 'weekly' });
    expect(screen.getByText(/Last 7 Days/)).toBeInTheDocument();

    renderChart({ volumeData: mockData, timeframe: 'monthly' });
    expect(screen.getByText(/Last 30 Days/)).toBeInTheDocument();
  });

  it('allows muscle group selection', () => {
    renderChart({ volumeData: mockData, timeframe: 'weekly' });
    const select = screen.getByRole('combobox');
    fireEvent.mouseDown(select);
    
    // Check if all muscle group options are present
    expect(screen.getByText('Total Volume')).toBeInTheDocument();
    expect(screen.getByText('Chest Volume')).toBeInTheDocument();
    expect(screen.getByText('Back Volume')).toBeInTheDocument();
    expect(screen.getByText('Legs Volume')).toBeInTheDocument();
  });
});
