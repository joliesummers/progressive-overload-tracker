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
import MuscleVolumeChart from './MuscleVolumeChart';
import VolumeProgressionChart from './VolumeProgressionChart';
import MuscleStatusCard from './MuscleStatusCard';
import { useAnalytics } from '../../hooks/useAnalytics';
import { useMuscleVolume } from '../../hooks/useMuscleVolume';
import { useVolumeProgression } from '../../hooks/useVolumeProgression';

interface AnalyticsDashboardProps {
  // muscleData: MuscleTrackingStatus[];
}

const AnalyticsDashboard: React.FC = () => {
  const [timeframe, setTimeframe] = useState<'weekly' | 'monthly'>('weekly');
  const { data: muscleData, isLoading: muscleLoading, error: muscleError } = useAnalytics();
  const { data: volumeData, isLoading: volumeLoading, error: volumeError } = useMuscleVolume(timeframe);
  const { data: progressionData, isLoading: progressionLoading, error: progressionError } = useVolumeProgression(timeframe);

  const handleTimeframeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newTimeframe: 'weekly' | 'monthly' | null,
  ) => {
    if (newTimeframe !== null) {
      setTimeframe(newTimeframe);
    }
  };

  const isLoading = muscleLoading || volumeLoading || progressionLoading;
  const error = muscleError || volumeError || progressionError;

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
          <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
            <MuscleStatusCard data={muscleData || []} />
          </Paper>
          <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
            <MuscleVolumeChart
              volumeData={volumeData || []}
              timeframe={timeframe}
            />
          </Paper>
          <Paper elevation={3} sx={{ p: 2 }}>
            <VolumeProgressionChart
              data={progressionData?.length ? progressionData : []}
            />
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <MuscleActivationChart data={muscleData || []} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalyticsDashboard;
