import { statsApi } from './api';

export const getStatisticsSummary = async () => {
  try {
    const response = await statsApi.get('/user-reservations');
    console.log('API Response:', response.data);

    const mostActiveUser = response.data.user_reservations.reduce((prev, current) => 
      (prev.reservation_count > current.reservation_count) ? prev : current
    );

    return {
      total_reservations: response.data.total_reservations || 0,
      most_active_user: mostActiveUser ? `${mostActiveUser.username} (${mostActiveUser.reservation_count})` : 'N/A',
      average_reservations: response.data.user_reservations.length > 0
        ? (response.data.total_reservations / response.data.user_reservations.length).toFixed(2)
        : 'N/A'
    };
  } catch (error) {
    console.error('Error fetching statistics summary:', error);
    console.error('Error details:', error.response?.data);
    throw error;
  }
};

export const getAdminDashboardStats = async () => {
  try {
    const response = await statsApi.get('/admin/dashboard-stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching admin dashboard stats:', error);
    throw error;
  }
};