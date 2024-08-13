import { feedbackApi } from './api';

export const getFeedbacks = async (page = 1, limit = 10, venueId = null, userId = null) => {
  try {
    const params = { page, limit };
    if (venueId) params.venue_id = venueId;
    if (userId) params.user_id = userId;
    const response = await feedbackApi.get('', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching feedbacks:', error);
    throw error;
  }
};

export const getMyFeedbacks = async (page = 1, limit = 10) => {
  try {
    const response = await feedbackApi.get('/my', { params: { page, limit } });
    return response.data;
  } catch (error) {
    console.error('Error fetching my feedbacks:', error);
    throw error;
  }
};

export const getFeedbackById = async (feedbackId) => {
  try {
    const response = await feedbackApi.get(`/${feedbackId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching feedback:', error);
    throw error;
  }
};

export const createFeedback = async (feedbackData) => {
  try {
    const response = await feedbackApi.post('', feedbackData);
    return response.data;
  } catch (error) {
    console.error('Error creating feedback:', error);
    throw error;
  }
};

export const updateFeedback = async (feedbackId, feedbackData) => {
  try {
    const response = await feedbackApi.put(`/${feedbackId}`, feedbackData);
    return response.data;
  } catch (error) {
    console.error('Error updating feedback:', error);
    throw error;
  }
};

export const deleteFeedback = async (feedbackId) => {
  try {
    await feedbackApi.delete(`/${feedbackId}`);
  } catch (error) {
    console.error('Error deleting feedback:', error);
    throw error;
  }
};

export const replyToFeedback = async (feedbackId, reply) => {
  try {
    const response = await feedbackApi.post(`/${feedbackId}/reply`, { reply });
    return response.data;
  } catch (error) {
    console.error('Error replying to feedback:', error);
    throw error;
  }
};