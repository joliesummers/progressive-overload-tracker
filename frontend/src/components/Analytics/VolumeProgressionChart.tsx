import React from 'react';
import { Box, Typography } from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { VolumeProgressionData } from '../../types/exercise';

interface VolumeProgressionChartProps {
  data: VolumeProgressionData[];
}

const VolumeProgressionChart: React.FC<VolumeProgressionChartProps> = ({ data }) => {
  // Handle empty or undefined data
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography sx={{ color: '#fff' }}>
          No volume progression data available
        </Typography>
      </Box>
    );
  }

  // Format volume numbers for display
  const formatVolume = (value: number) => {
    if (typeof value !== 'number' || isNaN(value)) return '0';
    return new Intl.NumberFormat().format(Math.round(value));
  };

  // Group data by date and muscle
  const groupedData = data.reduce((acc, item) => {
    const date = new Date(item.date).toLocaleDateString();
    if (!acc[date]) {
      acc[date] = { date };
    }
    acc[date][item.muscle_name] = item.total_volume;
    return acc;
  }, {} as Record<string, any>);

  const chartData = Object.values(groupedData);
  const muscles = Array.from(new Set(data.map(item => item.muscle_name)));
  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#ff0000', '#0088FE', '#00C49F'];

  return (
    <Box sx={{ width: '100%', height: 400, bgcolor: '#1e1e1e' }}>
      <Typography variant="h6" gutterBottom sx={{ color: '#fff' }}>
        Volume Progression
      </Typography>
      <ResponsiveContainer>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            dataKey="date" 
            tick={{ fill: '#fff', fontSize: 12 }}
            stroke="rgba(255,255,255,0.3)"
          />
          <YAxis 
            tick={{ fill: '#fff', fontSize: 12 }}
            stroke="rgba(255,255,255,0.3)"
            tickFormatter={formatVolume}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e1e1e',
              border: '1px solid rgba(255,255,255,0.1)',
              color: '#fff',
              fontSize: 12,
            }}
            labelStyle={{ color: '#fff', fontWeight: 'bold' }}
            formatter={formatVolume}
          />
          <Legend 
            wrapperStyle={{ color: '#fff' }}
            formatter={(value) => <span style={{ color: '#fff', fontSize: 12 }}>{value}</span>}
          />
          {muscles.map((muscle, index) => (
            <Line
              key={muscle}
              type="monotone"
              dataKey={muscle}
              stroke={colors[index % colors.length]}
              name={muscle}
              dot={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default VolumeProgressionChart;
