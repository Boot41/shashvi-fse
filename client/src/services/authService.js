import axios from 'axios';
import { API_BASE_URL, ENDPOINTS } from './config';

const authService = {
    /**
     * Login user and get access token
     * @param {string} username 
     * @param {string} password 
     * @returns {Promise} Response with tokens
     */
    login: async (username, password) => {
        try {
            const response = await axios.post(`${API_BASE_URL}${ENDPOINTS.LOGIN}`, {
                username,
                password
            });
            
            // Store tokens
            localStorage.setItem('accessToken', response.data.access);
            localStorage.setItem('refreshToken', response.data.refresh);
            
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    /**
     * Register new user
     * @param {Object} userData - User registration data
     * @returns {Promise} Response with user data
     */
    register: async (userData) => {
        try {
            const response = await axios.post(`${API_BASE_URL}${ENDPOINTS.REGISTER}`, userData);
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    /**
     * Refresh access token using refresh token
     * @returns {Promise} Response with new access token
     */
    refreshToken: async () => {
        try {
            const refreshToken = localStorage.getItem('refreshToken');
            if (!refreshToken) {
                throw new Error('No refresh token available');
            }

            const response = await axios.post(`${API_BASE_URL}${ENDPOINTS.REFRESH_TOKEN}`, {
                refresh: refreshToken
            });

            localStorage.setItem('accessToken', response.data.access);
            return response.data;
        } catch (error) {
            // If refresh fails, logout user
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            throw error.response?.data || error.message;
        }
    },

    /**
     * Logout user
     */
    logout: () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
    },

    /**
     * Check if user is authenticated
     * @returns {boolean}
     */
    isAuthenticated: () => {
        return !!localStorage.getItem('accessToken');
    }
};

export default authService;
