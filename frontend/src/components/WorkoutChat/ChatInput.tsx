import React, { useState, KeyboardEvent } from 'react';
import { 
  Box, 
  TextField, 
  Button,
  IconButton, 
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

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    handleSend();
  };

  const handleVoice = () => {
    if (isRecording) {
      onStopRecording?.();
    } else {
      onStartRecording?.();
    }
  };

  return (
    <Box 
      sx={{ 
        p: 2, 
        bgcolor: 'background.paper',
        borderTop: 1,
        borderColor: 'divider'
      }}
    >
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe your workout..."
            disabled={isLoading}
            helperText="Describe your workout or ask for advice"
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'background.paper',
                color: 'text.primary',
                '& input, & textarea': {
                  color: 'text.primary',
                  '&::placeholder': {
                    color: 'text.secondary',
                    opacity: '1 !important',
                  },
                },
                '& fieldset': {
                  borderColor: 'rgba(255,255,255,0.1)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255,255,255,0.2)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'primary.main',
                },
              },
              '& .MuiFormHelperText-root': {
                color: 'text.secondary',
                marginLeft: 0,
                marginTop: 1,
              },
            }}
          />
          {onStartRecording && onStopRecording && (
            <Tooltip title={isRecording ? 'Stop Recording' : 'Start Recording'}>
              <IconButton 
                onClick={handleVoice}
                color={isRecording ? "error" : "primary"}
                disabled={isLoading}
                sx={{
                  bgcolor: 'background.paper',
                  '&:hover': {
                    bgcolor: 'background.default',
                  },
                }}
              >
                {isRecording ? <StopIcon /> : <MicIcon />}
              </IconButton>
            </Tooltip>
          )}
          <Button
            variant="contained"
            color="primary"
            onClick={handleSend}
            disabled={!message.trim() || isLoading}
            sx={{
              height: 'fit-content',
              alignSelf: 'flex-start',
              minWidth: '80px',
            }}
          >
            Send
          </Button>
        </Box>
      </form>
    </Box>
  );
};

export default ChatInput;
