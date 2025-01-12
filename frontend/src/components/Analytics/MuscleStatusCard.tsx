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

  const getCoverageColor = (rating: string) => {
    switch (rating) {
      case 'Excellent':
        return theme.palette.success.main;
      case 'Good':
        return theme.palette.info.main;
      case 'Adequate':
        return theme.palette.warning.main;
      case 'Not enough':
        return theme.palette.error.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const getRecoveryColor = (recovery: number) => {
    if (recovery >= 0.8) return theme.palette.success.main;
    if (recovery >= 0.5) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {status.muscle_name}
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Coverage Rating
          </Typography>
          <Chip
            label={status.coverage_rating}
            sx={{
              bgcolor: getCoverageColor(status.coverage_rating),
              color: 'white',
              mt: 1,
            }}
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Recovery Status
          </Typography>
          <LinearProgress
            variant="determinate"
            value={status.recovery_status * 100}
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

        <Box sx={{ mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Weekly Volume: {status.weekly_volume.toFixed(1)}
          </Typography>
        </Box>

        <Box>
          <Typography variant="body2" color="text.secondary">
            Last Worked: {status.last_worked.toLocaleDateString()}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default MuscleStatusCard;
