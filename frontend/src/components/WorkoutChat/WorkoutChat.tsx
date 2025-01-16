import React, { useState } from 'react';
import { Box, TextField, Button, Paper, Typography, CircularProgress } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import { ENDPOINTS } from '../../config';

interface Message {
  text: string;
  sender: 'user' | 'bot';
}

export const WorkoutChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const theme = useTheme();

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, sender: 'user' as const };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      console.log('Sending request to:', ENDPOINTS.CHAT);
      const response = await fetch(ENDPOINTS.CHAT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      console.log('Response status:', response.status);
      if (!response.ok) {
        const errorData = await response.text();
        console.error('Server error:', errorData);
        console.error('Response headers:', Object.fromEntries(response.headers.entries()));
        throw new Error(`Server error: ${response.status} - ${errorData}`);
      }

      const data = await response.json();
      console.log('Received response:', data);
      const botMessage = { text: data.message, sender: 'bot' as const };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error details:', {
        error,
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      });
      const errorMessage = { 
        text: `Error: ${error instanceof Error ? error.message : 'Failed to connect to the chat service'}`, 
        sender: 'bot' as const 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper 
        elevation={3} 
        sx={{ 
          flex: 1, 
          mb: 2, 
          p: 2, 
          overflowY: 'auto',
          bgcolor: theme.palette.background.default
        }}
      >
        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
              mb: 2
            }}
          >
            <Paper
              elevation={1}
              sx={{
                p: 2,
                maxWidth: '70%',
                bgcolor: message.sender === 'user' 
                  ? theme.palette.primary.main 
                  : theme.palette.background.paper,
                color: message.sender === 'user' 
                  ? theme.palette.primary.contrastText 
                  : theme.palette.text.primary
              }}
            >
              <Typography>{message.text}</Typography>
            </Paper>
          </Box>
        ))}
      </Paper>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isLoading}
          sx={{ flex: 1 }}
        />
        <Button
          variant="contained"
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          sx={{ minWidth: 100 }}
        >
          {isLoading ? <CircularProgress size={24} /> : <SendIcon />}
        </Button>
      </Box>
    </Box>
  );
};
