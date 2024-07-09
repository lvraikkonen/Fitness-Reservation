import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';
const STATS_URL = 'http://localhost:8000/stats';
const FEEDBACK_URL = 'http://localhost:8000/feedback';
const RESERVATION_URL = 'http://localhost:8000/api/v1/reservations'
const VENUE_URL = 'http://localhost:8000/api/v1/venues'

const addAuthInterceptor = (apiInstance) => {
  apiInstance.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  });
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
  baseURL: RESERVATION_URL,
  headers: { 'Content-Type': 'application/json' },
}));

export const venueApi = addAuthInterceptor(axios.create({  
  baseURL: VENUE_URL,
  headers: { 'Content-Type': 'application/json' },
}));

export default api;