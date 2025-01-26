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
        <Typography sx={{ color: '#fff' }}>
          No muscle tracking data available
        </Typography>
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

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Recovering':
        return 'error.main';
      case 'Partially Recovered':
        return 'warning.main';
      case 'Fully Recovered':
        return 'success.main';
      default:
        return 'text.secondary';
    }
  };

  return (
    <Box sx={{ width: '100%', bgcolor: '#1e1e1e', p: 2 }}>
      <Typography variant="h6" gutterBottom sx={{ color: '#fff', mb: 3 }}>
        Muscle Recovery Status
      </Typography>
      <Grid container spacing={2}>
        {data.map((muscle) => {
          const recoveryStatus = getRecoveryStatus(muscle.days_since_last_trained);
          const recoveryPercentage = getRecoveryPercentage(muscle.days_since_last_trained);

          return (
            <Grid item xs={12} sm={6} md={4} key={muscle.muscle_name}>
              <Card sx={{ 
                bgcolor: '#2d2d2d', 
                boxShadow: 1,
                '& .MuiTypography-root': {
                  color: '#fff'
                }
              }}>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#fff', mb: 2 }}>
                    {muscle.muscle_name}
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body1" sx={{ color: '#fff', mb: 1 }}>
                      Last Trained: {formatDate(muscle.last_trained)}
                    </Typography>
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        color: '#fff',
                        mt: 1,
                        fontWeight: 500,
                      }}
                    >
                      Status: {recoveryStatus}
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={recoveryPercentage} 
                        sx={{
                          bgcolor: 'rgba(255,255,255,0.1)',
                          '& .MuiLinearProgress-bar': {
                            bgcolor: getStatusColor(recoveryStatus)
                          }
                        }}
                      />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
};

export default MuscleStatusCard;
