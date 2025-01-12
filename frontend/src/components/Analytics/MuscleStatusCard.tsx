import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Box,
  Chip,
  useTheme,
} from '@mui/material';
import { MuscleTrackingStatus } from '../../types/exercise';

interface MuscleStatusCardProps {
  status: MuscleTrackingStatus;
}

const MuscleStatusCard: React.FC<MuscleStatusCardProps> = ({ status }) => {
  const theme = useTheme();

  const getRecoveryColor = (status: string) => {
    switch (status) {
      case 'Recovered':
        return theme.palette.success.main;
      case 'Recovering':
        return theme.palette.warning.main;
      case 'Fatigued':
        return theme.palette.error.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const getVolumeColor = (trend: number) => {
    if (trend >= 4.0) return theme.palette.success.main;
    if (trend >= 2.5) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const getRecoveryPercentage = (status: string) => {
    switch (status) {
      case 'Recovered':
        return 100;
      case 'Recovering':
        return 60;
      case 'Fatigued':
        return 30;
      default:
        return 0;
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {status.muscle_name}
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Recovery Status
          </Typography>
          <Chip
            label={status.recovery_status}
            sx={{
              bgcolor: getRecoveryColor(status.recovery_status),
              color: 'white',
              mt: 1,
            }}
          />
          <LinearProgress
            variant="determinate"
            value={getRecoveryPercentage(status.recovery_status)}
            sx={{
              mt: 1,
              height: 8,
              borderRadius: 4,
              bgcolor: theme.palette.grey[200],
              '& .MuiLinearProgress-bar': {
                bgcolor: getRecoveryColor(status.recovery_status),
              },
            }}
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Volume Trend
          </Typography>
          <LinearProgress
            variant="determinate"
            value={(status.volume_trend / 5) * 100}
            sx={{
              mt: 1,
              height: 8,
              borderRadius: 4,
              bgcolor: theme.palette.grey[200],
              '& .MuiLinearProgress-bar': {
                bgcolor: getVolumeColor(status.volume_trend),
              },
            }}
          />
        </Box>

        <Box sx={{ mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Sets Last Week: {status.sets_last_week}
          </Typography>
        </Box>

        <Box>
          <Typography variant="body2" color="text.secondary">
            Last Workout: {new Date(status.last_workout).toLocaleDateString()}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default MuscleStatusCard;
