import axios from 'axios';

const API_URL = 'http://localhost:8000';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await axios.post(`${API_URL}/token`, {
    username: credentials.email,
    password: credentials.password,
  });
  
  // Store the token for future requests
  localStorage.setItem('token', response.data.access_token);
  
  return response.data;
};

// Add the token to all future requests
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Example of a protected request
export const getCurrentUser = async () => {
  const response = await axios.get(`${API_URL}/me`);
  return response.data;
};
