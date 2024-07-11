import { reservationApi } from "./api";
import { venueApi } from "./api";
import dayjs from 'dayjs';
import { getCurrentUser } from "./auth";

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
    sport_venue_name: item.sport_venue_name || 'Unknown sport venue',
    venue_name: item.venue_name || 'Unknown venue',
    status: item.status
  }));
};

export const fetchUserReservations = async (venueId = null, page = 1, pageSize = 20) => {
  try {
    const user = getUser();
    if (!user || !user.id) {
      console.error('User information is missing. Please log in again.');
      throw new Error('User not found or user ID is missing');
    }

    const params = { 
      user_id: user.id,
      page,
      page_size: pageSize
    };
    if (venueId) {
      params.venue_id = venueId;
    }

    const response = await reservationApi.get('/user-reservations', { params });

    console.log('Raw user reservations:', response.data);

    const { reservations, total_count, page: currentPage, page_size } = response.data;

    if (!Array.isArray(reservations)) {
      console.error('Unexpected data format received from server');
      return { reservations: [], total_count: 0, page: currentPage, page_size };
    }

    const transformedData = transformReservationData(reservations);
    console.log('Transformed user reservations:', transformedData);

    return { 
      reservations: transformedData, 
      total_count,
      page: currentPage, 
      page_size 
    };
  } catch (error) {
    console.error('Error fetching user reservations:', error);
    
    if (error.response) {
      console.error(`Failed to fetch reservations: ${error.response.data.detail || 'Unknown error'}`);
    } else if (error.request) {
      console.error('No response received from server. Please check your network connection.');
    } else {
      console.error('An unexpected error occurred. Please try again.');
    }

    return { reservations: [], total_count: 0, page: 1, page_size: 20 };
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
    console.log('Sending reservation data:', enhancedReservationData);
    const response = await reservationApi.post('/reservations', enhancedReservationData);
    return response.data;
  } catch (error) {
    console.error('Error creating reservation:', error);
    if (error.response && error.response.data) {
      console.error('Server error details:', error.response.data);
    }
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