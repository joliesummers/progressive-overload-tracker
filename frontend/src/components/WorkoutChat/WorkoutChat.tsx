import React, { useState } from 'react';
import { Box, TextField, Button, Paper, Typography, CircularProgress } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import { bedrockService } from '../../services/bedrock';

interface Message {
  text: string;
  sender: 'user' | 'bot';
  isStreaming?: boolean;
  muscleData?: any;
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
      // Add an initial empty bot message that will be updated with streaming content
      setMessages(prev => [...prev, { text: '', sender: 'bot', isStreaming: true }]);

      await bedrockService.sendMessage(
        input,
        // Handle text chunks
        (chunk: string) => {
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage.sender === 'bot') {
              lastMessage.text += chunk;
            }
            return newMessages;
          });
        },
        // Handle muscle data
        (muscleData: any) => {
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage.sender === 'bot') {
              lastMessage.muscleData = muscleData;
            }
            return newMessages;
          });
        }
      );

      // Mark the message as no longer streaming
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage.sender === 'bot') {
          lastMessage.isStreaming = false;
        }
        return newMessages;
      });

    } catch (error) {
      console.error('Error in chat:', error);
      setMessages(prev => [
        ...prev,
        {
          text: error instanceof Error ? error.message : 'An error occurred',
          sender: 'bot'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (message: Message, index: number) => {
    return (
      <Box
        key={index}
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start',
          mb: 2,
        }}
      >
        <Paper
          elevation={1}
          sx={{
            p: 2,
            maxWidth: '70%',
            backgroundColor: message.sender === 'user' ? theme.palette.primary.main : theme.palette.background.paper,
            color: message.sender === 'user' ? theme.palette.primary.contrastText : theme.palette.text.primary,
          }}
        >
          <Typography sx={{ color: '#fff' }}>{message.text}</Typography>
          {message.isStreaming && (
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
              <CircularProgress size={16} />
              <Typography variant="caption" sx={{ ml: 1, color: 'rgba(255,255,255,0.7)' }}>
                Thinking...
              </Typography>
            </Box>
          )}
          {message.muscleData && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" color="textSecondary" sx={{ color: '#fff' }}>
                Muscle Activation Analysis:
              </Typography>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', color: '#fff' }}>
                {JSON.stringify(message.muscleData, null, 2)}
              </pre>
            </Box>
          )}
        </Paper>
      </Box>
    );
  };

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: '#000000',
        p: 3,
      }}
    >
      <Typography variant="h5" gutterBottom sx={{ color: '#fff', mb: 3 }}>
        Workout Chat
      </Typography>
      <Box
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          bgcolor: '#1e1e1e',
          borderRadius: 2,
          overflow: 'hidden',
        }}
      >
        <Box
          sx={{
            flexGrow: 1,
            overflow: 'auto',
            p: 2,
            bgcolor: '#1e1e1e',
          }}
        >
          {messages.map((message, index) => renderMessage(message, index))}
          {isLoading && (
            <Typography sx={{ color: 'rgba(255,255,255,0.7)', p: 2, textAlign: 'center' }}>
              Thinking...
            </Typography>
          )}
        </Box>
        <Box 
          sx={{ 
            borderTop: 1, 
            borderColor: 'divider',
            bgcolor: '#1e1e1e',
            p: 2,
          }}
        >
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="Describe your workout..."
              multiline
              maxRows={4}
              disabled={isLoading}
              sx={{ color: '#fff' }}
            />
            <Button
              variant="contained"
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              endIcon={<SendIcon />}
              sx={{ color: '#fff' }}
            >
              Send
            </Button>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};
