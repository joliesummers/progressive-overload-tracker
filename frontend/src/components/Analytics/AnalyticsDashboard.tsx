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
      <Box sx={{ p: 3, bgcolor: '#000000' }}>
        <Typography color="error">Error loading analytics data</Typography>
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
    <Box sx={{ 
      minHeight: '100vh',
      bgcolor: '#000000',
      p: 3,
    }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <ToggleButtonGroup
          value={timeframe}
          exclusive
          onChange={handleTimeframeChange}
          sx={{
            bgcolor: '#1e1e1e',
            '& .MuiToggleButton-root': {
              color: 'text.primary',
              borderColor: 'rgba(255,255,255,0.1)',
              '&.Mui-selected': {
                bgcolor: 'primary.dark',
                color: '#fff',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
              },
            },
          }}
        >
          <ToggleButton value="weekly">Weekly</ToggleButton>
          <ToggleButton value="monthly">Monthly</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper
            sx={{
              p: 3,
              bgcolor: '#1e1e1e',
              '& .MuiTypography-root': { color: '#fff' }
            }}
          >
            <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
              Muscle Status
            </Typography>
            <MuscleStatusCard data={muscleData || []} />
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper
            sx={{
              p: 3,
              bgcolor: '#1e1e1e',
              '& .MuiTypography-root': { color: '#fff' }
            }}
          >
            <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
              Muscle Recovery Status
            </Typography>
            <MuscleStatusCard data={muscleData || []} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              bgcolor: '#1e1e1e',
              '& .MuiTypography-root': { color: '#fff' }
            }}
          >
            <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
              Muscle Activation
            </Typography>
            <MuscleActivationChart data={muscleData || []} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              bgcolor: '#1e1e1e',
              '& .MuiTypography-root': { color: '#fff' }
            }}
          >
            <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
              Muscle Volume Distribution
            </Typography>
            <MuscleVolumeChart volumeData={volumeData || []} timeframe={timeframe} />
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper
            sx={{
              p: 3,
              bgcolor: '#1e1e1e',
              '& .MuiTypography-root': { color: '#fff' }
            }}
          >
            <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
              Volume Progression
            </Typography>
            <VolumeProgressionChart data={progressionData || []} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalyticsDashboard;
