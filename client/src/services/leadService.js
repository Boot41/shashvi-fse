import axios from 'axios';
import { API_BASE_URL, ENDPOINTS, getAuthHeader } from './config';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Add auth header interceptor
api.interceptors.request.use(
    (config) => {
        const headers = getAuthHeader();
        config.headers = { ...config.headers, ...headers };
        return config;
    },
    (error) => Promise.reject(error)
);

const leadService = {
    /**
     * Get all leads
     * @returns {Promise} Response with leads data
     */
    getLeads: async () => {
        try {
            const response = await api.get(ENDPOINTS.LEADS);
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    /**
     * Get lead by ID
     * @param {number} leadId 
     * @returns {Promise} Response with lead data
     */
    getLeadById: async (leadId) => {
        try {
            const response = await api.get(`${ENDPOINTS.LEADS}${leadId}/`);
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    /**
     * Import leads from CSV file
     * @param {File} file - CSV file
     * @returns {Promise} Response with import results
     */
    importLeads: async (file) => {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await api.post(ENDPOINTS.IMPORT_LEADS, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    /**
     * Process leads with optional filters
     * @param {Object} filters - Optional filters (status, industry)
     * @returns {Promise} Response with processing results
     */
    processLeads: async (filters = {}) => {
        try {
            const params = new URLSearchParams(filters);
            const response = await api.post(`${ENDPOINTS.PROCESS_LEADS}?${params}`);
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    /**
     * Generate messages for a lead
     * @param {number} leadId 
     * @returns {Promise} Response with generated messages
     */
    generateMessages: async (leadId) => {
        try {
            const response = await api.post(ENDPOINTS.GENERATE_MESSAGES(leadId));
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    /**
     * Test message generation with sample data
     * @param {Object} testData - Sample lead data
     * @returns {Promise} Response with test messages
     */
    testMessageGeneration: async (testData) => {
        try {
            const response = await api.post(ENDPOINTS.TEST_MESSAGE, testData);
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    }
};

export default leadService;
