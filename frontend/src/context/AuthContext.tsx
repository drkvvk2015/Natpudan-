import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { Box, CircularProgress } from '@mui/material';
import apiClient from '../services/apiClient';

interface AuthContextType {
  user: any;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (token: string, user: any) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export { AuthContext };

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Initialize auth state on mount and listen for storage events
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    console.log('AuthContext: Initial auth check on mount...', storedToken ? 'Token exists' : 'No token');
    
    if (storedToken) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
      setToken(storedToken);
      setIsAuthenticated(true);
      
      // Restore user data from localStorage
      if (storedUser) {
        try {
          const userData = JSON.parse(storedUser);
          setUser(userData);
          console.log('AuthContext: User restored from localStorage:', userData.email);
        } catch (e) {
          console.error('AuthContext: Failed to parse stored user data', e);
          // If user data is corrupt, clear everything
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setToken(null);
          setIsAuthenticated(false);
        }
      }
      console.log('AuthContext: User authenticated on mount');
    } else {
      console.log('AuthContext: No stored token, user not authenticated');
    }
    
    setLoading(false);

    // Listen for storage changes (useful for multi-tab scenarios)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'token') {
        const newToken = e.newValue;
        console.log('AuthContext: Storage event detected, token changed');
        if (newToken) {
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
          setToken(newToken);
          setIsAuthenticated(true);
          
          // Also check for updated user data
          const storedUser = localStorage.getItem('user');
          if (storedUser) {
            try {
              setUser(JSON.parse(storedUser));
            } catch (e) {
              console.error('Failed to parse user data from storage event');
            }
          }
        } else {
          delete apiClient.defaults.headers.common['Authorization'];
          setToken(null);
          setUser(null);
          setIsAuthenticated(false);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []); // Empty dependency array - only run once on mount

  const login = (newToken: string, userData: any) => {
    console.log('AuthContext: Login called with token and user data', userData);
    localStorage.setItem('token', newToken);
    localStorage.setItem('user', JSON.stringify(userData)); // Persist user data
    setToken(newToken);
    setUser(userData);
    setIsAuthenticated(true);
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    
    // Dispatch custom event to notify components about auth state change
    window.dispatchEvent(new CustomEvent('authStateChanged', { 
      detail: { isAuthenticated: true, user: userData } 
    }));
    console.log('AuthContext: User logged in successfully:', userData.email);
  };

  const logout = () => {
    console.log('AuthContext: Logout called');
    localStorage.removeItem('token');
    localStorage.removeItem('user'); // Also remove user data
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    delete apiClient.defaults.headers.common['Authorization'];
    
    // Dispatch custom event to notify components about auth state change
    window.dispatchEvent(new CustomEvent('authStateChanged', { 
      detail: { isAuthenticated: false, user: null } 
    }));
    console.log('AuthContext: User logged out successfully');
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, loading, login, logout }}>
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
          <CircularProgress />
        </Box>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
