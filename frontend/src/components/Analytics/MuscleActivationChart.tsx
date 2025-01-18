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
import { Box, Typography } from '@mui/material';
import { MuscleTrackingStatus } from '../../types/exercise';

interface MuscleActivationChartProps {
  data: MuscleTrackingStatus[];
}

const MuscleActivationChart: React.FC<MuscleActivationChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography>No muscle activation data available</Typography>
      </Box>
    );
  }

  // Transform data for radar chart
  const chartData = data.map(muscle => ({
    muscle: muscle.muscle_name,
    activity: 100 - muscle.days_since_last_trained, // Higher value means more recently trained
  }));

  return (
    <Box sx={{ width: '100%', height: 400 }}>
      <Typography variant="h6" gutterBottom>
        Muscle Activation Map
      </Typography>
      <ResponsiveContainer>
        <RadarChart data={chartData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="muscle" />
          <PolarRadiusAxis angle={30} domain={[0, 100]} />
          <Radar
            name="Activity Level"
            dataKey="activity"
            stroke="#8884d8"
            fill="#8884d8"
            fillOpacity={0.6}
          />
          <Tooltip />
        </RadarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default MuscleActivationChart;
