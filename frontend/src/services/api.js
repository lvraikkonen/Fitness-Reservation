import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';
const STATS_URL = 'http://localhost:8000/stats';
const FEEDBACK_URL = 'http://localhost:8000/feedback';

const api = axios.create({
  baseURL: API_URL,
});

export const statsApi = axios.create({  // 添加这个新的 API 实例
  baseURL: STATS_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const feedbackApi = axios.create({  // 添加这个新的 API 实例
  baseURL: FEEDBACK_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

export default api;