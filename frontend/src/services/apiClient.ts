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

// Add retry count to request config
interface RetryConfig extends InternalAxiosRequestConfig {
  _retry?: number;
  _retryDelay?: number;
}

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config: RetryConfig) => {
    const token = localStorage.getItem('token');
    
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
      console.log('[KEY] API Request Interceptor:', {
        url: config.url,
        token: `${token.substring(0, 20)}...`,
        authHeaderSet: true,
        fullAuthHeader: config.headers['Authorization'].substring(0, 30) + '...'
      });
    } else {
      console.warn('[WARNING] API Request WITHOUT token:', {
        url: config.url,
        hasToken: false
      });
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
      
      console.log(`Retrying request (attempt ${config._retry}/3) after ${delay}ms...`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
      
      return apiClient(config);
    }

    return Promise.reject(error);
  }
);

export default apiClient;

// Lightweight health check helpers for UI status indicators
export async function checkBackendHealth(): Promise<{ ok: boolean; status?: any }> {
  try {
    const res = await axios.get(`${API_BASE_URL}/health`, { timeout: 5000 });
    return { ok: res.status === 200, status: res.data };
  } catch (e) {
    return { ok: false };
  }
}

export async function checkBackendDetailed(): Promise<{ ok: boolean; status?: any }> {
  try {
    const res = await axios.get(`${API_BASE_URL}/health/detailed`, { timeout: 5000 });
    return { ok: res.status === 200, status: res.data };
  } catch (e) {
    return { ok: false };
  }
}
