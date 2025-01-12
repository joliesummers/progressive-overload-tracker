import axios from 'axios';
import { API_BASE_URL, ENDPOINTS } from '../config';

export interface ExerciseAnalysis {
  muscles_worked: {
    muscle: string;
    activation_level: string;
  }[];
  recommendations: string[];
  form_tips: string[];
}

export const analyzeExercise = async (exerciseDescription: string): Promise<ExerciseAnalysis> => {
  try {
    const response = await axios.post(`${API_BASE_URL}${ENDPOINTS.ANALYZE_EXERCISE}`, {
      exercise_description: exerciseDescription,
    });
    return response.data;
  } catch (error: any) {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error('Failed to analyze exercise. Please try again.');
  }
};
