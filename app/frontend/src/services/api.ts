import axios from 'axios';
import type { ChatRequest, ChatResponse, HealthCheckResponse, SchemesResponse } from '../types';

// Use Vite env variable or fallback to empty string (uses Vite proxy in dev)
// In dev: Vite proxies /api/* → http://localhost:8000, so baseURL must be empty
// On Vercel: VITE_API_URL is not set, Vercel rewrites /api/* → Railway
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    return config;
  },
  (error) => {
    console.error('[API] Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Unknown error occurred';
    console.error('[API] Response Error:', message);
    return Promise.reject(new Error(message));
  }
);

export const chatApi = {
  /**
   * Send a chat query to the assistant
   */
  async sendMessage(query: string, sessionId?: string): Promise<ChatResponse> {
    const request: ChatRequest = {
      query,
      session_id: sessionId,
    };
    
    const response = await api.post<ChatResponse>('/api/v1/chat', request);
    return response.data;
  },

  /**
   * Get health status of the backend
   */
  async getHealth(): Promise<HealthCheckResponse> {
    const response = await api.get<HealthCheckResponse>('/api/v1/health');
    return response.data;
  },

  /**
   * Get list of available schemes
   */
  async getSchemes(): Promise<SchemesResponse> {
    const response = await api.get<SchemesResponse>('/api/v1/schemes');
    return response.data;
  },
};

export default api;
