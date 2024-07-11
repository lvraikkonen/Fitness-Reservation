import api from './api';

export const login = async (credentials) => {
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  const response = await api.post('/users/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
  const { access_token, user } = response.data;
  localStorage.setItem('token', access_token);
  localStorage.setItem('user', JSON.stringify(user));
  return user;
};

export const register = async (userData) => {
  const response = await api.post('/users/register', userData);
  return response.data;
};

export const requestPasswordReset = async (email) => {
  const response = await api.post('/users/reset-password-request', { email });
  return response.data;
};

export const resetPassword = async (token, newPassword) => {
  const response = await api.post('/users/reset-password', { token, new_password: newPassword });
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

export const getCurrentUser = () => {
  return JSON.parse(localStorage.getItem('user'));
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};

export const updateUserProfile = async (profileData) => {
  try {
    const response = await api.put('/users/me', profileData);
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  } catch (error) {
    console.error('Error updating user profile:', error);
    throw error;
  }
};

export const updateUserSettings = async (settingsData) => {
  try {
    const response = await api.put('/users/me', settingsData);
    const currentUser = getCurrentUser();
    localStorage.setItem('user', JSON.stringify({ ...currentUser, settings: response.data }));
    return response.data;
  } catch (error) {
    console.error('Error updating user settings:', error);
    throw error;
  }
};

export const checkAuthStatus = async () => {
  const token = localStorage.getItem('token');
  if (!token) return null;
  
  try {
    const response = await api.get('/users/me');
    const user = response.data;
    localStorage.setItem('user', JSON.stringify(user));
    return user;
  } catch (error) {
    console.error('Failed to verify auth status:', error);
    logout();
    return null;
  }
};