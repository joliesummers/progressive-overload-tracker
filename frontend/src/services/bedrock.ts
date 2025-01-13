import axios from 'axios';
import { API_BASE_URL, ENDPOINTS } from '../config';

interface ChatMessage {
  content: string;
  role: 'user' | 'assistant';
}

interface ChatResponse {
  message: string;
  error?: string;
}

export const sendMessage = async (message: string): Promise<ChatResponse> => {
  try {
    const response = await axios.post(`${API_BASE_URL}${ENDPOINTS.CHAT}`, 
      {
        message,
        model: 'anthropic.claude-3-haiku-20240307-v1:0', // Claude 3.5 Haiku model ID
      },
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    return {
      message: response.data.message,
    };
  } catch (error: any) {
    console.error('Error sending message to Claude:', error);
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to send message';
    throw new Error(errorMessage);
  }
};

export const bedrockService = {
  sendMessage,
};
