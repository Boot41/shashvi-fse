export const API_BASE_URL = 'http://localhost:8001/api';

export const ENDPOINTS = {
    // Auth endpoints
    LOGIN: '/token/',
    REGISTER: '/register/',
    REFRESH_TOKEN: '/token/refresh/',

    // Lead endpoints
    LEADS: '/leads/',
    IMPORT_LEADS: '/leads/import/',
    PROCESS_LEADS: '/leads/process/',
    GENERATE_MESSAGES: (leadId) => `/leads/${leadId}/generate-messages/`,
    TEST_MESSAGE: '/leads/test-message/',
};

export const getAuthHeader = () => {
    const token = localStorage.getItem('accessToken');
    return token ? { Authorization: `Bearer ${token}` } : {};
};
