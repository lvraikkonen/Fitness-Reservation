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
  const { access_token } = response.data;
  localStorage.setItem('token', access_token);
  return response.data;
};

export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const logout = () => {
  localStorage.removeItem('token');
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