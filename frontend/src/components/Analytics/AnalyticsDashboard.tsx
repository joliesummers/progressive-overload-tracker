import React, { useState } from 'react';
import {
  Grid,
  Paper,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  Box,
  CircularProgress,
} from '@mui/material';
import MuscleActivationChart from './MuscleActivationChart';
import MuscleStatusCard from './MuscleStatusCard';
import { useAnalytics } from '../../hooks/useAnalytics';

interface AnalyticsDashboardProps {
  // muscleData: MuscleTrackingStatus[];
}

const AnalyticsDashboard: React.FC = () => {
  const [timeframe, setTimeframe] = useState<'weekly' | 'monthly'>('weekly');
  const { data: muscleData, isLoading, error } = useAnalytics();

  const handleTimeframeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newTimeframe: 'weekly' | 'monthly' | null,
  ) => {
    if (newTimeframe !== null) {
      setTimeframe(newTimeframe);
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error">Error loading analytics data. Please try again later.</Typography>
      </Box>
    );
  }

  if (!muscleData || muscleData.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>No workout data available. Start tracking your workouts to see analytics!</Typography>
      </Box>
    );
  }

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
