import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import apiClient from '../services/apiClient';

interface AuthContextType {
  user: any;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, user: any) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!localStorage.getItem('token'));

  // Initialize auth state on mount and listen for storage events
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    console.log('AuthContext: Initial token check on mount...', storedToken ? 'Token exists' : 'No token');
    
    if (storedToken && storedToken !== token) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
      setToken(storedToken);
      setIsAuthenticated(true);
      console.log('AuthContext: User authenticated on mount');
    } else if (!storedToken && isAuthenticated) {
      setIsAuthenticated(false);
      console.log('AuthContext: User not authenticated');
    }

    // Listen for storage changes (useful for multi-tab scenarios)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'token') {
        const newToken = e.newValue;
        console.log('AuthContext: Storage event detected, token changed');
        if (newToken) {
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
          setToken(newToken);
          setIsAuthenticated(true);
        } else {
          delete apiClient.defaults.headers.common['Authorization'];
          setToken(null);
          setIsAuthenticated(false);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = (newToken: string, userData: any) => {
    console.log('AuthContext: Login called with token and user data');
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setUser(userData);
    setIsAuthenticated(true);
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    
    // Dispatch custom event to notify components about auth state change
    window.dispatchEvent(new CustomEvent('authStateChanged', { 
      detail: { isAuthenticated: true, user: userData } 
    }));
    console.log('AuthContext: User logged in successfully');
  };

  const logout = () => {
    console.log('AuthContext: Logout called');
    localStorage.removeItem('token');
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
    <AuthContext.Provider value={{ user, token, isAuthenticated, login, logout }}>
      {children}
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
