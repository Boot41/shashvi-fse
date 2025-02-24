import { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('accessToken');
    if (token) {
      const userData = JSON.parse(localStorage.getItem('user'));
      setUser(userData);
    }
    setLoading(false);
  }, []);

  const login = async (email, password, rememberMe) => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/login/', {
        email,
        password
      });

      const { user: userData, tokens } = response.data;
      
      setUser(userData);
      localStorage.setItem('accessToken', tokens.access);
      localStorage.setItem('refreshToken', tokens.refresh);
      
      if (rememberMe) {
        localStorage.setItem('user', JSON.stringify(userData));
      }

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'An error occurred during login'
      };
    }
  };

  const register = async (username, email, password) => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/register/', {
        username,
        email,
        password
      });

      const { user: userData, tokens } = response.data;
      
      setUser(userData);
      localStorage.setItem('accessToken', tokens.access);
      localStorage.setItem('refreshToken', tokens.refresh);
      localStorage.setItem('user', JSON.stringify(userData));

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'An error occurred during registration'
      };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  };

  const refreshToken = async () => {
    try {
      const refresh = localStorage.getItem('refreshToken');
      const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
        refresh_token: refresh
      });

      localStorage.setItem('accessToken', response.data.access);
      return true;
    } catch (error) {
      logout();
      return false;
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    refreshToken
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
