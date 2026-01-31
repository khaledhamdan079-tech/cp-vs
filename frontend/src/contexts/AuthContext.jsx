import { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/client';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await apiClient.get('/api/auth/me');
      setUser(response.data);
    } catch (error) {
      // Handle 403 (unconfirmed user) differently
      if (error.response?.status === 403) {
        // User is not confirmed, but keep token for confirmation status check
        // Don't clear token, but set user to null
        setUser(null);
      } else {
        localStorage.removeItem('token');
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const checkConfirmationStatus = async () => {
    try {
      const response = await apiClient.get('/api/auth/confirmation-status');
      return response.data;
    } catch (error) {
      console.error('Error checking confirmation status:', error);
      throw error;
    }
  };

  const login = async (handle, password) => {
    const response = await apiClient.post('/api/auth/login', {
      handle,
      password,
    });
    localStorage.setItem('token', response.data.access_token);
    await fetchUser();
    return response.data;
  };

  const register = async (handle, password) => {
    try {
      const response = await apiClient.post('/api/auth/register', {
        handle: handle.trim(),
        password,
      });
      // Token is already stored in Register component, but we return the data
      return response.data;
    } catch (error) {
      console.error('Register API error:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, fetchUser, checkConfirmationStatus }}>
      {children}
    </AuthContext.Provider>
  );
};
