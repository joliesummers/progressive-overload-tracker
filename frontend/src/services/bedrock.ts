import axios from 'axios';
import { ENDPOINTS, API_BASE_URL } from '../config';

interface ChatMessage {
  content: string;
  role: 'user' | 'assistant';
}

interface ChatResponse {
  message?: string;
  type: 'message' | 'muscle_data' | 'error';
  muscle_data?: any;
  error?: string;
}

export const sendMessage = async (
  message: string,
  onChunk: (chunk: string) => void,
  onMuscleData?: (data: any) => void
): Promise<void> => {
  try {
    const response = await axios({
      method: 'post',
      url: `${API_BASE_URL}${ENDPOINTS.CHAT}`,
      data: { message },
      headers: {
        'Content-Type': 'application/json',
      }
    });

    const data = response.data;
    
    // Handle message
    if (data.message) {
      onChunk(data.message);
    }
    
    // Handle muscle data
    if (data.muscle_data && onMuscleData) {
      onMuscleData(data.muscle_data);
    }
    
  } catch (error: any) {
    console.error('Error sending message to Claude:', error);
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to send message';
    throw new Error(errorMessage);
  }
};

export const bedrockService = {
  sendMessage,
};
