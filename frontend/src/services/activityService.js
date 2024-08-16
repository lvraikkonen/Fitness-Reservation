import { userApi } from './api';
import dayjs from 'dayjs';

export const fetchRecentActivities = async (limit = 5) => {
  try {
    const response = await userApi.get('/recent-activities', { params: { limit } });
    return transformActivitiesData(response.data);
  } catch (error) {
    console.error('Error fetching recent activities:', error);
    throw error;
  }
};

const transformActivitiesData = (rawData) => {
  return rawData.map(activity => ({
    id: activity.id,
    activity_type: activity.activity_type,
    timestamp: dayjs(activity.timestamp).format('YYYY-MM-DD HH:mm:ss'),
    venue_name: activity.venue_name,
    sport_venue_name: activity.sport_venue_name,
    date: dayjs(activity.date).format('YYYY-MM-DD'),
    start_time: dayjs(activity.start_time, 'HH:mm:ss').format('HH:mm'),
    end_time: dayjs(activity.end_time, 'HH:mm:ss').format('HH:mm'),
    status: activity.status
  }));
};