import React, { useState } from 'react';
import {
  Grid,
  Paper,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  Box,
} from '@mui/material';
import MuscleActivationChart from './MuscleActivationChart';
import MuscleStatusCard from './MuscleStatusCard';
import { MuscleTrackingStatus } from '../../types/exercise';

interface AnalyticsDashboardProps {
  muscleData: MuscleTrackingStatus[];
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ muscleData }) => {
  const [timeframe, setTimeframe] = useState<'weekly' | 'monthly'>('weekly');

  const handleTimeframeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newTimeframe: 'weekly' | 'monthly' | null,
  ) => {
    if (newTimeframe !== null) {
      setTimeframe(newTimeframe);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">Workout Analytics</Typography>
        <ToggleButtonGroup
          value={timeframe}
          exclusive
          onChange={handleTimeframeChange}
          aria-label="timeframe"
        >
          <ToggleButton value="weekly" aria-label="weekly">
            Weekly
          </ToggleButton>
          <ToggleButton value="monthly" aria-label="monthly">
            Monthly
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <MuscleActivationChart
            muscleData={muscleData}
            timeframe={timeframe}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recovery Status
            </Typography>
            <Grid container spacing={2}>
              {muscleData.map((muscle) => (
                <Grid item xs={12} key={muscle.muscle_name}>
                  <MuscleStatusCard status={muscle} />
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalyticsDashboard;
