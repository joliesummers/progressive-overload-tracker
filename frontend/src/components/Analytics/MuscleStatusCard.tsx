import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
} from '@mui/material';
import { MuscleTrackingStatus } from '../../types/exercise';

interface MuscleStatusCardProps {
  data: MuscleTrackingStatus[];
}

const MuscleStatusCard: React.FC<MuscleStatusCardProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography>No muscle tracking data available</Typography>
      </Box>
    );
  }

  // Calculate recovery percentage (inverse of days since last trained)
  const getRecoveryPercentage = (days: number) => {
    const maxDays = 7; // Consider fully recovered after 7 days
    return Math.max(0, Math.min(100, ((maxDays - days) / maxDays) * 100));
  };

  // Get recovery status text
  const getRecoveryStatus = (days: number) => {
    if (days <= 1) return 'Recovering';
    if (days <= 3) return 'Partially Recovered';
    return 'Fully Recovered';
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Muscle Recovery Status
      </Typography>
      <Grid container spacing={2}>
        {data.map((muscle) => (
          <Grid item xs={12} sm={6} md={4} key={muscle.muscle_name}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {muscle.muscle_name}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Last trained: {new Date(muscle.last_trained).toLocaleDateString()}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Days since: {muscle.days_since_last_trained}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    Recovery Status: {getRecoveryStatus(muscle.days_since_last_trained)}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={getRecoveryPercentage(muscle.days_since_last_trained)}
                    sx={{ mt: 1 }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default MuscleStatusCard;
