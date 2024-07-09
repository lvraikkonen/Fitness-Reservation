import { reservationApi } from "./api";
import { venueApi } from "./api";
import dayjs from 'dayjs';

// const RESERVATION_URL = 'http://localhost:8000/api/v1/reservations'
// /api/v1/reservations/venues/{venue_id}/calendar
// const VENUE_URL = 'http://localhost:8000/api/v1/venues'

const getUser = () => {
  return JSON.parse(localStorage.getItem('user'));
};


export const fetchVenues = async () => {
  const response = await venueApi.get('/venues');
  return response.data;
};

export const fetchVenueCalendar = async (venueId, startDate, endDate, page = 1, pageSize = 10) => {
  try {
    const response = await reservationApi.get(`/venues/${venueId}/calendar`, {
      params: {
        start_date: startDate ? dayjs(startDate).format('YYYY-MM-DD') : undefined,
        end_date: endDate ? dayjs(endDate).format('YYYY-MM-DD') : undefined,
        page,
        page_size: pageSize
      }
    });
    // 添加数据验证
    const data = response.data;
    return {
      calendar_data: data.calendar_data || {},
      total_pages: data.total_pages || 1,
      current_page: data.current_page || 1,
      page_size: data.page_size || 10
    };
  } catch (error) {
    console.error('Error fetching venue calendar:', error);
    throw error;
  }
};

const transformReservationData = (rawData) => {
  return rawData.map(item => ({
    id: item.id,
    date: item.date || item.reservation_date,
    start_time: item.start_time,
    end_time: item.end_time,
    venue_name: item.venue_name || 'Unknown venue',
    status: item.status
  }));
};

export const fetchUserReservations = async (venueId) => {
  try {
    const response = await reservationApi.get('/user-reservations', {
      params: { venue_id: venueId }
    });
    console.log('Raw user reservations:', response.data);
    const transformedData = transformReservationData(response.data);
    console.log('Transformed user reservations:', transformedData);
    return transformedData;
  } catch (error) {
    console.error('Error fetching user reservations:', error);
    throw error;
  }
};

export const createReservation = async (venueId, reservationData) => {
  try {
    const user = getUser();
    const enhancedReservationData = {
      ...reservationData,
      user_id: user.id,
      venue_id: venueId,
    };
    const response = await reservationApi.post('/reservations', enhancedReservationData);
    return response.data;
  } catch (error) {
    console.error('Error creating reservation:', error);
    throw error;
  }
};

export const cancelReservation = async (reservationId) => {
  try {
    await reservationApi.delete(`/reservations/${reservationId}`);
  } catch (error) {
    console.error('Error cancelling reservation:', error);
    throw error;
  }
};