import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_URL = `${BASE_URL}/api/v1`;
const STATS_URL = `${BASE_URL}/stats`;
const FEEDBACK_URL = `${BASE_URL}/feedback`;

axios.defaults.baseURL = BASE_URL;

const addAuthInterceptor = (apiInstance) => {
  apiInstance.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  });

  apiInstance.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && error.response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return apiInstance;
};

const api = addAuthInterceptor(axios.create({ baseURL: API_URL }));

export const statsApi = addAuthInterceptor(axios.create({
  baseURL: STATS_URL,
  headers: { 'Content-Type': 'application/json' },
}));

export const feedbackApi = addAuthInterceptor(axios.create({
  baseURL: FEEDBACK_URL,
  headers: { 'Content-Type': 'application/json' },
}));

export const reservationApi = addAuthInterceptor(axios.create({
  baseURL: `${API_URL}/reservations`,
  headers: { 'Content-Type': 'application/json' },
}));

export const venueApi = addAuthInterceptor(axios.create({  
  baseURL: `${API_URL}/venues`,
  headers: { 'Content-Type': 'application/json' },
}));

// 新增用户相关的 API
export const userApi = addAuthInterceptor(axios.create({
  baseURL: `${API_URL}/users`,
  headers: { 'Content-Type': 'application/json' },
}));

export default api;