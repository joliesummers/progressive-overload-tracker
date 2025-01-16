import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Box, Typography } from '@mui/material';
import { MuscleVolumeData } from '../../types/exercise';

interface MuscleVolumeChartProps {
  volumeData: MuscleVolumeData[];
  timeframe: 'weekly' | 'monthly';
}

const MuscleVolumeChart: React.FC<MuscleVolumeChartProps> = ({ volumeData, timeframe }) => {
  if (!volumeData || volumeData.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography>No volume data available</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', height: 400 }}>
      <Typography variant="h6" gutterBottom>
        Muscle Volume (Last {timeframe === 'weekly' ? '7 Days' : '30 Days'})
      </Typography>
      <ResponsiveContainer>
        <BarChart data={volumeData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="muscle_name" />
          <YAxis label={{ value: 'Total Volume (kg)', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Bar dataKey="total_volume" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default MuscleVolumeChart;
