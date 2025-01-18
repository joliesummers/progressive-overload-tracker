import React from 'react';
import { render, screen } from '@testing-library/react';
import MuscleVolumeChart from '../MuscleVolumeChart';

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

describe('MuscleVolumeChart', () => {
  it('renders chart title correctly', () => {
    render(
      <MuscleVolumeChart volumeData={mockVolumeData} timeframe="weekly" />
    );
    
    expect(screen.getByText(/Muscle Volume \(Last 7 Days\)/)).toBeInTheDocument();
  });

  it('renders monthly title when timeframe is monthly', () => {
    render(
      <MuscleVolumeChart volumeData={mockVolumeData} timeframe="monthly" />
    );
    
    expect(screen.getByText(/Muscle Volume \(Last 30 Days\)/)).toBeInTheDocument();
  });

  it('displays no data message when data is empty', () => {
    render(
      <MuscleVolumeChart volumeData={[]} timeframe="weekly" />
    );
    
    expect(screen.getByText('No volume data available')).toBeInTheDocument();
  });

  it('renders chart with data', () => {
    const { container } = render(
      <MuscleVolumeChart volumeData={mockVolumeData} timeframe="weekly" />
    );
    
    // Check if Recharts components are rendered
    expect(container.querySelector('.recharts-wrapper')).toBeInTheDocument();
    expect(container.querySelector('.recharts-bar')).toBeInTheDocument();
  });
});
