import { venueApi } from "./api";

export const getVenues = async (skip = 0, limit = 100) => {
  try {
    const response = await venueApi.get('/venues', {
      params: {
        skip: skip,
        limit: limit
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching venues:', error);
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