import React, { useState, useRef, useEffect } from 'react';
import { Box, Paper, Typography, CircularProgress } from '@mui/material';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { analyzeExercise } from '../../services/exercise';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

const WorkoutChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const analysis = await analyzeExercise(text);
      
      // Create response message
      const responseText = formatAnalysis(analysis);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        isUser: false,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error: any) {
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: error.message || 'Sorry, I could not analyze your exercise. Please try again.',
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatAnalysis = (analysis: any) => {
    let response = '';

    // Add muscles worked
    if (analysis.muscles_worked?.length > 0) {
      response += '🎯 Muscles Worked:\n';
      analysis.muscles_worked.forEach((muscle: any) => {
        response += `- ${muscle.muscle} (${muscle.activation_level})\n`;
      });
      response += '\n';
    }

    // Add recommendations
    if (analysis.recommendations?.length > 0) {
      response += '💡 Recommendations:\n';
      analysis.recommendations.forEach((rec: string) => {
        response += `- ${rec}\n`;
      });
      response += '\n';
    }

    // Add form tips
    if (analysis.form_tips?.length > 0) {
      response += '✨ Form Tips:\n';
      analysis.form_tips.forEach((tip: string) => {
        response += `- ${tip}\n`;
      });
    }

    return response.trim();
  };

  return (
    <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6">Exercise Analysis Chat</Typography>
      </Box>

      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
      </Box>

      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <ChatInput 
          onSendMessage={handleSendMessage} 
          isLoading={isLoading}
          isRecording={isRecording}
          setIsRecording={setIsRecording}
        />
      </Box>
    </Paper>
  );
};

export default WorkoutChat;
