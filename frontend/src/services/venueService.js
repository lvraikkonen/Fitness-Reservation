import { venueApi } from "./api";

export const getVenues = async (params = {}) => {
  try {
    const response = await venueApi.get('/venues', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching venues:', error);
    throw error;
  }
};

export const getVenueDetails = async (venueId) => {
  try {
    const response = await venueApi.get(`/venues/${venueId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching venue details for id ${venueId}:`, error);
    throw error;
  }
};

export const searchVenues = async (query = '', sportType = null, limit = 10) => {
  try {
    const params = { limit };
    if (query.trim() !== '') {
      params.query = query;
    }
    if (sportType && sportType !== 'all') {
      params.sport_type = sportType;
    }
    console.log('Sending request with params:', params);
    const response = await venueApi.get('/venues/search', { params });
    console.log('Received response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error searching venues:', error);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
      console.error('Response headers:', error.response.headers);
    }
    throw error;
  }
};

export const getVenueAvailability = async (venueId, date) => {
  try {
    const response = await venueApi.get(`/venues/${venueId}/availability`, {
      params: { date }
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching venue availability for id ${venueId}:`, error);
    throw error;
  }
};

export const createVenue = async (venueData) => {
  try {
    const response = await venueApi.post('/venues', venueData);
    return response.data;
  } catch (error) {
    console.error('Error creating venue:', error);
    throw error;
  }
};

export const updateVenue = async (venueId, venueData) => {
  try {
    const response = await venueApi.put(`/venues/${venueId}`, venueData);
    return response.data;
  } catch (error) {
    console.error('Error updating venue:', error);
    throw error;
  }
};

export const deleteVenue = async (venueId) => {
  try {
    await venueApi.delete(`/venues/${venueId}`);
  } catch (error) {
    console.error('Error deleting venue:', error);
    throw error;
  }
};