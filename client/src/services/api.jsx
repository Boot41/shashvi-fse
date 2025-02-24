import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Token management
const TokenService = {
  getLocalAccessToken() {
    return localStorage.getItem('accessToken');
  },
  getLocalRefreshToken() {
    return localStorage.getItem('refreshToken');
  },
  setLocalAccessToken(token) {
    localStorage.setItem('accessToken', token);
  },
  setLocalRefreshToken(token) {
    localStorage.setItem('refreshToken', token);
  },
  removeTokens() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  },
};

// Add request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = TokenService.getLocalAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = TokenService.getLocalRefreshToken();
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const response = await axios.post(`${API_URL}/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        TokenService.setLocalAccessToken(access);

        // Update the original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (err) {
        // If refresh token fails, logout user
        TokenService.removeTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

// Auth services
export const auth = {
  register: async (userData) => {
    const response = await api.post('/register/', userData);
    return response;
  },
  login: async (credentials) => {
    const response = await api.post('/token/', credentials);
    if (response.data.access) {
      TokenService.setLocalAccessToken(response.data.access);
      TokenService.setLocalRefreshToken(response.data.refresh);
    }
    return response;
  },
  logout: () => {
    TokenService.removeTokens();
  },
  refreshToken: async () => {
    const refreshToken = TokenService.getLocalRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token found');
    }
    const response = await api.post('/token/refresh/', {
      refresh: refreshToken,
    });
    if (response.data.access) {
      TokenService.setLocalAccessToken(response.data.access);
    }
    return response;
  },
};

// Lead services
export const leads = {
  getAll: () => api.get('/leads/'),
  import: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/leads/import/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  process: () => api.post('/leads/process/'),
  generateMessages: (leadId) => api.post('/leads/test-message/', { lead_id: leadId }),
};

export default api;
