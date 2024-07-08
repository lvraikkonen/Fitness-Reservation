import { feedbackApi } from './api';

export const submitFeedback = async (feedbackData) => {
  try {
    const user = JSON.parse(localStorage.getItem('user'));
    const enhancedFeedbackData = {
      ...feedbackData,
      user_id: user.id,
      venue_id: 1,  // 这里应该是实际的场馆 ID，可能需要从其他地方获取
    };
    const response = await feedbackApi.post('/', enhancedFeedbackData);
    return response.data;
  } catch (error) {
    console.error('Error submitting feedback:', error);
    throw error;
  }
};

export const getFeedbackList = async () => {
  try {
    const response = await feedbackApi.get('/');
    return response.data;
  } catch (error) {
    console.error('Error fetching feedback list:', error);
    throw error;
  }
};