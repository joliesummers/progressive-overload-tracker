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
        <Typography sx={{ color: '#fff' }}>
          No muscle activation data available
        </Typography>
      </Box>
    );
  }

  // Calculate the maximum volume for normalization
  const maxVolume = Math.max(...data.map(muscle => muscle.weekly_volume));

  // Transform data for radar chart
  const chartData = data.map(muscle => {
    // Ensure all numeric values are valid
    const weeklyVolume = Number(muscle.weekly_volume) || 0;
    const exerciseCount = Number(muscle.exercise_count) || 0;
    const recoveryStatus = Number(muscle.recovery_status) || 0;

    // Normalize volume to 0-100 scale
    const normalizedVolume = maxVolume > 0 ? (weeklyVolume / maxVolume) * 100 : 0;
    
    // Calculate activation score based on multiple factors
    const volumeScore = normalizedVolume;
    const frequencyScore = Math.min(exerciseCount * 25, 100); // 4+ exercises = 100%
    const recoveryScore = recoveryStatus * 100;
    
    // Weighted average of scores
    const activationScore = (volumeScore * 0.4) + (frequencyScore * 0.4) + (recoveryScore * 0.2);

    return {
      muscle: muscle.muscle_name || 'Unknown',
      activation: Math.round(activationScore) || 0,
      volume: Math.round(normalizedVolume) || 0,
      frequency: Math.round(frequencyScore) || 0,
      recovery: Math.round(recoveryScore) || 0,
      tooltipContent: {
        volume: weeklyVolume,
        exercises: exerciseCount,
        status: muscle.status || 'Unknown'
      }
    };
  });

  const formatTooltip = (value: number, name: string, props: any) => {
    if (name === 'activation' && props.payload.tooltipContent) {
      const { volume, exercises, status } = props.payload.tooltipContent;
      return [
        <div key="tooltip">
          <div>Volume: {new Intl.NumberFormat().format(volume)}</div>
          <div>Exercises: {exercises}</div>
          <div>Status: {status}</div>
        </div>,
        'Details'
      ];
    }
    return [`${Math.round(value)}%`, name];
  };

  return (
    <Box sx={{ width: '100%', height: 400, bgcolor: '#1e1e1e' }}>
      <Typography variant="h6" gutterBottom sx={{ color: '#fff' }}>
        Muscle Activation Levels
      </Typography>
      <ResponsiveContainer>
        <RadarChart data={chartData}>
          <PolarGrid stroke="rgba(255,255,255,0.1)" />
          <PolarAngleAxis 
            dataKey="muscle" 
            tick={{ fill: '#fff', fontSize: 12 }}
            stroke="rgba(255,255,255,0.3)"
          />
          <PolarRadiusAxis 
            angle={30} 
            domain={[0, 100]}
            tick={{ fill: '#fff', fontSize: 12 }}
            stroke="rgba(255,255,255,0.3)"
          />
          <Radar
            name="Activation"
            dataKey="activation"
            stroke="#90caf9"
            fill="#90caf9"
            fillOpacity={0.6}
          />
          <Tooltip 
            formatter={formatTooltip}
            contentStyle={{
              backgroundColor: '#1e1e1e',
              border: '1px solid rgba(255,255,255,0.1)',
              color: '#fff',
              fontSize: 12,
            }}
            labelStyle={{ color: '#fff', fontWeight: 'bold' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default MuscleActivationChart;
