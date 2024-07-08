import api from './api';

export const getVenues = async () => {
  try {
    const response = await api.get('/venues/venues');
    return response.data;
  } catch (error) {
    console.error('Error fetching venues:', error);
    throw error;
  }
};