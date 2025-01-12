import React from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { Box, Paper, Typography, useTheme } from '@mui/material';
import { MuscleTrackingStatus } from '../../types/exercise';

interface MuscleActivationChartProps {
  muscleData: MuscleTrackingStatus[];
  timeframe: 'weekly' | 'monthly';
}

const MuscleActivationChart: React.FC<MuscleActivationChartProps> = ({
  muscleData,
  timeframe,
}) => {
  const theme = useTheme();

  const chartData = muscleData.map((muscle) => ({
    muscle: muscle.muscle_name,
    volume: timeframe === 'weekly' ? muscle.weekly_volume : muscle.monthly_volume,
    fullMark: 100,
  }));

  return (
    <Paper elevation={3} sx={{ p: 2, height: '400px' }}>
      <Typography variant="h6" gutterBottom>
        Muscle Activation {timeframe === 'weekly' ? 'This Week' : 'This Month'}
      </Typography>
      <Box sx={{ width: '100%', height: '100%' }}>
        <ResponsiveContainer>
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
            <PolarGrid />
            <PolarAngleAxis
              dataKey="muscle"
              tick={{ fill: theme.palette.text.primary }}
            />
            <PolarRadiusAxis
              angle={30}
              domain={[0, 100]}
              tick={{ fill: theme.palette.text.primary }}
            />
            <Radar
              name="Volume"
              dataKey="volume"
              stroke={theme.palette.primary.main}
              fill={theme.palette.primary.main}
              fillOpacity={0.6}
            />
            <Tooltip />
          </RadarChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default MuscleActivationChart;
