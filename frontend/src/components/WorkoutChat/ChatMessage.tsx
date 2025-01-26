import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp?: Date;  
}

const formatTimestamp = (timestamp: Date | undefined) => {
  if (!timestamp) return '';
  return new Date(timestamp).toLocaleTimeString();
};

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
      <Box
        sx={{
          maxWidth: '70%',
          bgcolor: isUser ? 'primary.main' : '#2d2d2d',
          borderRadius: 2,
          p: 2,
        }}
      >
        <Typography
          variant="body1"
          sx={{
            color: '#fff',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          {message}
        </Typography>
        {timestamp && (
          <Typography
            variant="caption"
            sx={{
              color: 'rgba(255,255,255,0.7)',
              display: 'block',
              mt: 1,
              textAlign: isUser ? 'right' : 'left',
            }}
          >
            {formatTimestamp(timestamp)}
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default ChatMessage;
