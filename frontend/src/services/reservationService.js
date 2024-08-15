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

export const fetchVenueCalendar = async (venueId, startDate, endDate) => {
  try {
    const response = await reservationApi.get(`/venues/${venueId}/availability`, {
      params: { start_date: startDate, end_date: endDate }
    });

    console.log("raw venue availability response is :", response)
    
    // 检查响应数据结构
    if (!response.data || !Array.isArray(response.data)) {
      console.error('Unexpected response format:', response.data);
      return {};
    }

    // 将数据转换为所需的格式
    const formattedData = response.data.reduce((acc, dayData) => {
      const { date, venue_id, venue_name, time_slots } = dayData;
      
      acc[date] = time_slots.map(slot => ({
        id: `${venue_id}-${date}-${slot.start_time}`, // 创建一个唯一ID
        startTime: slot.start_time,
        endTime: slot.end_time,
        availableCapacity: slot.available_capacity,
        totalCapacity: slot.total_capacity,
        venueName: venue_name
      }));

      return acc;
    }, {});

    return formattedData;
  } catch (error) {
    console.error('Error fetching venue calendar:', error);
    throw error;
  }
};

// 处理预约数据
const transformReservationData = (rawData) => {
  return rawData.map(item => ({
    id: item.id,
    date: dayjs(item.date).format('YYYY-MM-DD'),
    start_time: dayjs(item.actual_start_time, 'HH:mm:ss').format('HH:mm'),
    end_time: dayjs(item.actual_end_time, 'HH:mm:ss').format('HH:mm'),
    sport_venue_name: item.sport_venue_name || 'Unknown sport venue',
    venue_name: item.venue_name || 'Unknown venue',
    status: item.status
  }));
};

// 处理详细的预约数据
const transformDetailedReservationData = (rawData) => {
  return {
    id: rawData.id,
    userId: rawData.user_id,
    venueId: rawData.venue_id,
    venueAvailableTimeSlotId: rawData.venue_available_time_slot_id,
    status: rawData.status,
    date: dayjs(rawData.date).format('YYYY-MM-DD'),
    actualStartTime: dayjs(rawData.actual_start_time, 'HH:mm:ss').format('HH:mm'),
    actualEndTime: dayjs(rawData.actual_end_time, 'HH:mm:ss').format('HH:mm'),
    isRecurring: rawData.is_recurring,
    venueName: rawData.venue_name || 'Unknown venue',
    recurringReservationId: rawData.recurring_reservation_id,
    createdAt: dayjs(rawData.created_at).format('YYYY-MM-DD HH:mm:ss'),
    updatedAt: dayjs(rawData.updated_at).format('YYYY-MM-DD HH:mm:ss'),
    cancelledAt: rawData.cancelled_at ? dayjs(rawData.cancelled_at).format('YYYY-MM-DD HH:mm:ss') : null,
    checkedInAt: rawData.checked_in_at ? dayjs(rawData.checked_in_at).format('YYYY-MM-DD HH:mm:ss') : null,
    sportVenueName: rawData.sport_venue_name || 'Unknown sport venue',
    userName: rawData.user_name || 'Unknown user',
    venueAvailableTimeSlotStart: dayjs(rawData.venue_available_time_slot_start, 'HH:mm:ss').format('HH:mm'),
    venueAvailableTimeSlotEnd: dayjs(rawData.venue_available_time_slot_end, 'HH:mm:ss').format('HH:mm')
  };
};

export const fetchUserReservations = async (venueId = null, page = 1, pageSize = 20, dateRange = null) => {
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
    // Add date range parameters if provided
    if (dateRange && dateRange[0] && dateRange[1]) {
      params.start_date = dateRange[0].format('YYYY-MM-DD');
      params.end_date = dateRange[1].format('YYYY-MM-DD');
    }

    const response = await reservationApi.get('/user-reservations', { params });

    const { reservations, total_count, page: currentPage, page_size } = response.data;

    if (!Array.isArray(reservations)) {
      console.error('Unexpected data format received from server');
      return { reservations: [], total_count: 0, page: currentPage, page_size };
    }

    const transformedData = transformReservationData(reservations);

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

export const getAllReservations = async (page = 1, pageSize = 10) => {
  try {
    const response = await reservationApi.get('/reservations', {
      params: {
        skip: (page - 1) * pageSize,
        limit: pageSize
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching all reservations:', error);
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
      status: reservationData.status || 'pending',
      is_recurring: reservationData.is_recurring || false,
      recurring_pattern: reservationData.recurring_pattern || null,
      recurrence_end_date: reservationData.recurrence_end_date || null,
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
    const response = await reservationApi.delete(`/reservations/${reservationId}`);
    return response.data;
  } catch (error) {
    console.error('Error cancelling reservation:', error);
    throw error;
  }
};

export const confirmReservation = async (reservationId) => {
  try {
    const response = await reservationApi.post(`/reservations/${reservationId}/confirm`);
    return response.data;
  } catch (error) {
    console.error('Error confirming reservation:', error);
    throw error;
  }
};

// 获取单个预约的详细信息
export const fetchReservationDetails = async (reservationId) => {
  try {
    const user = getUser();
    if (!user || !user.id) {
      throw new Error('User not found or user ID is missing');
    }

    const response = await reservationApi.get(`/reservations/${reservationId}`, {
      params: { user_id: user.id }
    });

    // console.log('Raw user reservations:', response.data);

    const transformedData = transformDetailedReservationData(response.data);

    // console.log('Transformed user reservation detail is:', transformedData);

    if (transformedData) {
      return transformedData;
    } else {
      throw new Error('Reservation data not found in the response');
    }
  } catch (error) {
    console.error('Error fetching reservation details:', error);
    throw error;
  }
};

// 生成 check-in token
export const generateCheckInToken = async (reservationId) => {
  try {
    const user = getUser();
    if (!user || !user.id) {
      throw new Error('User not found or user ID is missing');
    }

    const response = await reservationApi.get(`/reservations/${reservationId}/check-in-token`, {
      params: { user_id: user.id }
    });

    if (response.data && response.data.token) {
      return response.data.token;
    } else {
      throw new Error('Check-in token not found in the response');
    }
  } catch (error) {
    console.error('Error generating check-in token:', error);
    throw error;
  }
};

// 使用 token 或直接 check-in
export const checkInReservation = async (reservationId, token = null) => {
  try {
    const user = getUser();
    if (!user || !user.id) {
      throw new Error('User not found or user ID is missing');
    }

    let response;
    if (token) {
      // Using token for check-in
      response = await reservationApi.post('/reservations/check-in', {
        user_id: user.id,
        token: token
      });
    } else {
      // Direct check-in without token
      response = await reservationApi.post(`/reservations/${reservationId}/check-in`, {
        user_id: user.id
      });
    }

    if (response.data && response.data.success) {
      console.log('Check-in successful');
      return true;
    } else {
      throw new Error('Check-in failed');
    }
  } catch (error) {
    console.error('Error checking in reservation:', error);
    throw error;
  }
};