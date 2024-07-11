import React, { createContext, useState, useContext, useEffect } from 'react';
import { login, logout, checkAuthStatus, getCurrentUser } from '../services/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(getCurrentUser());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus().then(user => {
      setUser(user);
      setLoading(false);
    });
  }, []);

  const value = {
    user,
    loading,
    login: async (credentials) => {
      const user = await login(credentials);
      setUser(user);
      return user;
    },
    logout: () => {
      logout();
      setUser(null);
    },
    updateUser: (userData) => {
      setUser(userData);
    },
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);