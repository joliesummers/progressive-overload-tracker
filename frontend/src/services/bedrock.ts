import axios from 'axios';
import { ENDPOINTS } from '../config';

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
  let buffer = '';

  try {
    await axios({
      method: 'post',
      url: ENDPOINTS.CHAT, // Use relative URL to work with proxy
      data: { message },
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/x-ndjson',
      },
      responseType: 'text',
      onDownloadProgress: (progressEvent: any) => {
        if (!progressEvent.event?.target) {
          console.warn('No event target in progress event');
          return;
        }

        const response = progressEvent.event.target.response || '';
        const lines = response.slice(buffer.length).split('\n');
        
        buffer = response;  // Update buffer with full response

        for (const line of lines) {
          if (line.trim()) {
            try {
              const data: ChatResponse = JSON.parse(line);
              console.log('Received chunk:', data); // Debug log
              
              // Check if the message is a stringified JSON
              if (data.type === 'message' && data.message && typeof data.message === 'string') {
                try {
                  const parsedMessage = JSON.parse(data.message);
                  if (parsedMessage.type === 'error' && parsedMessage.error) {
                    console.error('Error from backend:', parsedMessage.error);
                    throw new Error(parsedMessage.error);
                  }
                  // If it's not an error, use the original message
                } catch (e) {
                  if (!(e instanceof SyntaxError)) {
                    throw e;
                  }
                  // If parsing fails, it's a regular message
                }
              }
              
              switch (data.type) {
                case 'message':
                  if (data.message) {
                    onChunk(data.message);
                  }
                  break;
                  
                case 'muscle_data':
                  if (data.muscle_data && onMuscleData) {
                    onMuscleData(data.muscle_data);
                  }
                  break;
                  
                case 'error':
                  if (data.error) {
                    console.error('Error from backend:', data.error);
                    throw new Error(data.error);
                  }
                  break;
              }
            } catch (e) {
              if (e instanceof SyntaxError) {
                console.debug('Incomplete JSON chunk, waiting for more data');
              } else {
                console.warn('Failed to parse chunk:', line, e);
              }
            }
          }
        }
      },
    });
  } catch (error: any) {
    console.error('Error sending message to Claude:', error);
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to send message';
    throw new Error(errorMessage);
  }
};

export const bedrockService = {
  sendMessage,
};
