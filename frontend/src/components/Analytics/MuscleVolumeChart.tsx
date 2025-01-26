import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
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
        <Typography sx={{ color: '#fff' }}>
          No volume data available
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', height: 400, bgcolor: '#1e1e1e' }}>
      <Typography variant="h6" gutterBottom sx={{ color: '#fff' }}>
        Muscle Volume (Last {timeframe === 'weekly' ? '7 Days' : '30 Days'})
      </Typography>
      <ResponsiveContainer>
        <BarChart data={volumeData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            dataKey="muscle_name" 
            tick={{ fill: '#fff', fontSize: 12 }}
            stroke="rgba(255,255,255,0.3)"
          />
          <YAxis 
            label={{ 
              value: 'Total Volume (kg)', 
              angle: -90, 
              position: 'insideLeft',
              fill: '#fff',
              fontSize: 12,
            }}
            tick={{ fill: '#fff', fontSize: 12 }}
            stroke="rgba(255,255,255,0.3)"
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e1e1e',
              border: '1px solid rgba(255,255,255,0.1)',
              color: '#fff',
              fontSize: 12,
            }}
            labelStyle={{ color: '#fff', fontWeight: 'bold' }}
          />
          <Legend 
            wrapperStyle={{ color: '#fff' }}
            formatter={(value) => <span style={{ color: '#fff', fontSize: 12 }}>{value}</span>}
          />
          <Bar dataKey="total_volume" fill="#90caf9" name="Volume" />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default MuscleVolumeChart;
