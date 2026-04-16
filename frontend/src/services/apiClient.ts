import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

// Direct API calls to backend (no proxy) with full URL
const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,  // Allow credentials for CORS
  timeout: 300000, // 5 minute timeout for large uploads
});

const createRequestId = (): string => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }

  return `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

// Add retry count to request config
interface RetryConfig extends InternalAxiosRequestConfig {
  _retry?: number;
  _retryDelay?: number;
}

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config: RetryConfig) => {
    const token = localStorage.getItem('token');
    config.headers['X-Request-ID'] = createRequestId();
    
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
      if (import.meta.env.DEV) {
        console.log('[Natpudan AI] Authenticated API request', { url: config.url });
      }
    }
    
    // Initialize retry count
    if (config._retry === undefined) {
      config._retry = 0;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - auto-retry on network errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as RetryConfig;
    
    // Don't retry if no config or if already retried 3 times
    if (!config || (config._retry && config._retry >= 3)) {
      return Promise.reject(error);
    }

    // Network errors that should be retried
    const shouldRetry = 
      !error.response || // Network error (no response)
      error.code === 'ECONNABORTED' || // Timeout
      error.code === 'ERR_NETWORK' || // Network error
      (error.response && [408, 429, 500, 502, 503, 504].includes(error.response.status)); // Server errors

    if (shouldRetry) {
      config._retry = (config._retry || 0) + 1;
      
      // Exponential backoff: 1s, 2s, 4s
      const delay = Math.min(1000 * Math.pow(2, config._retry - 1), 4000);
      
      if (import.meta.env.DEV) {
        console.log(`Retrying request (attempt ${config._retry}/3) after ${delay}ms...`);
      }
      
      await new Promise(resolve => setTimeout(resolve, delay));
      
      return apiClient(config);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
