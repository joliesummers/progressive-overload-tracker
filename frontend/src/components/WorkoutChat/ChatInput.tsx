import React, { useState, KeyboardEvent } from 'react';
import { 
  Box, 
  TextField, 
  IconButton, 
  Paper,
  useTheme,
  Tooltip
} from '@mui/material';
import { 
  Send as SendIcon,
  Mic as MicIcon,
  Stop as StopIcon 
} from '@mui/icons-material';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  onStartRecording?: () => void;
  onStopRecording?: () => void;
  isRecording?: boolean;
  isLoading?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onStartRecording,
  onStopRecording,
  isRecording = false,
  isLoading = false,
}) => {
  const [message, setMessage] = useState('');
  const theme = useTheme();

  const handleSend = () => {
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (event: KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey && !isLoading) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        backgroundColor: theme.palette.background.paper,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter your workout details..."
          disabled={isLoading}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
            },
          }}
        />
        {onStartRecording && onStopRecording && (
          <Tooltip title={isRecording ? 'Stop Recording' : 'Start Recording'}>
            <IconButton
              color={isRecording ? 'secondary' : 'primary'}
              onClick={isRecording ? onStopRecording : onStartRecording}
              disabled={isLoading}
            >
              {isRecording ? <StopIcon /> : <MicIcon />}
            </IconButton>
          </Tooltip>
        )}
        <IconButton
          color="primary"
          onClick={handleSend}
          disabled={!message.trim() || isLoading}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default ChatInput;
