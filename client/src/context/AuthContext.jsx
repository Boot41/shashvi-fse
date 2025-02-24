import { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../services';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    if (authService.isAuthenticated()) {
      const userData = JSON.parse(localStorage.getItem('user'));
      setUser(userData);
    }
    setLoading(false);
  }, []);

  const login = async (username, password, rememberMe) => {
    try {
      const response = await authService.login(username, password);
      
      // Extract user data from token payload
      const userData = {
        id: response.user_id,
        username
      };
      
      setUser(userData);
      
      if (rememberMe) {
        localStorage.setItem('user', JSON.stringify(userData));
      }

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.message || 'An error occurred during login'
      };
    }
  };

  const register = async (username, email, password) => {
    try {
      const userData = await authService.register({
        username,
        email,
        password
      });
      
      // After successful registration, login the user
      await login(username, password, true);

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.message || 'An error occurred during registration'
      };
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    localStorage.removeItem('user');
  };

  const refreshToken = async () => {
    try {
      await authService.refreshToken();
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
    refreshToken,
    isAuthenticated: authService.isAuthenticated
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
