import React from 'react';
import { Box, Paper, Typography, useTheme } from '@mui/material';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp: Date;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser, timestamp }) => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Paper
        elevation={1}
        sx={{
          maxWidth: '70%',
          p: 2,
          backgroundColor: isUser ? theme.palette.primary.main : theme.palette.background.paper,
          borderRadius: 2,
        }}
      >
        <Typography variant="body1" color={isUser ? 'white' : 'inherit'}>
          {message}
        </Typography>
        <Typography
          variant="caption"
          color={isUser ? 'rgba(255,255,255,0.7)' : 'text.secondary'}
          sx={{ display: 'block', mt: 1 }}
        >
          {timestamp.toLocaleTimeString()}
        </Typography>
      </Paper>
    </Box>
  );
};

export default ChatMessage;
