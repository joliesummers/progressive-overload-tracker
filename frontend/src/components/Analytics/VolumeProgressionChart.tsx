import React from 'react';
import { Box, Paper, Typography } from '@mui/material';
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
  // Group data by muscle name
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
  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#ff0000'];

  return (
    <Paper sx={{ p: 2, height: '400px' }}>
      <Typography variant="h6" gutterBottom>
        Volume Progression
      </Typography>
      <Box sx={{ width: '100%', height: '100%' }}>
        <ResponsiveContainer>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            {muscles.map((muscle, index) => (
              <Line
                key={muscle}
                type="monotone"
                dataKey={muscle}
                stroke={colors[index % colors.length]}
                name={muscle}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default VolumeProgressionChart;
