import axios from 'axios';
import { API_BASE_URL, ENDPOINTS } from '../config';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  full_name: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export const register = async (credentials: RegisterCredentials): Promise<User> => {
  try {
    const response = await axios.post(`${API_BASE_URL}${ENDPOINTS.REGISTER}`, credentials);
    return response.data;
  } catch (error: any) {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error('Registration failed. Please try again.');
  }
};

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  try {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);
    
    const response = await axios.post(`${API_BASE_URL}${ENDPOINTS.LOGIN}`, formData);
    
    // Store the token for future requests
    localStorage.setItem('token', response.data.access_token);
    
    return response.data;
  } catch (error: any) {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error('Login failed. Please check your credentials and try again.');
  }
};

// Add the token to all future requests
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getCurrentUser = async (): Promise<User> => {
  try {
    const response = await axios.get(`${API_BASE_URL}${ENDPOINTS.GET_USER}`);
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      throw new Error('Session expired. Please log in again.');
    }
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error('Failed to fetch user information.');
  }
};
