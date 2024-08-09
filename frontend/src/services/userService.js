import { userApi } from "./api";

// 模拟数据
const mockDashboardData = {
  username: "claus",
  upcomingReservations: [
    { id: 1, venueName: "Basketball Court", date: "2024-07-25", startTime: "14:00", endTime: "16:00" },
    { id: 2, venueName: "Tennis Court", date: "2024-07-27", startTime: "10:00", endTime: "12:00" },
    { id: 3, venueName: "Swimming Pool", date: "2024-07-30", startTime: "18:00", endTime: "19:00" },
  ],
  monthlyReservationCount: 5,
  monthlyReservationLimit: 10,
  recentActivities: [
    { id: 1, action: "Reserved Basketball Court", date: "2024-07-22" },
    { id: 2, action: "Cancelled Swimming Pool Reservation", date: "2024-07-20" },
    { id: 3, action: "Modified Tennis Court Reservation", date: "2024-07-18" },
  ],
  recommendedVenues: [
    { id: 1, name: "Gym", popularTime: "18:00 - 20:00" },
    { id: 2, name: "Yoga Studio", popularTime: "07:00 - 09:00" },
    { id: 3, name: "Badminton Court", popularTime: "12:00 - 14:00" },
  ],
};

// 配置标志：是否使用模拟数据
const USE_MOCK_DATA = false;

// 模拟API调用延迟
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// 数据转换函数
const transformDashboardData = (data) => {
  return {
    username: data.username,
    upcomingReservations: data.upcoming_reservations.map(res => ({
      id: res.id,
      venueName: res.venue_name,
      date: res.date,
      startTime: res.start_time,
      endTime: res.end_time
    })),
    monthlyReservationCount: data.monthly_reservation_count,
    monthlyReservationLimit: data.monthly_reservation_limit,
    recentActivities: data.recent_activities.map(activity => ({
      id: activity.id,
      date: activity.date,
      activity_type: activity.activity_type || 'unknown',
      activity_timestamp: activity.timestamp,
      venue_name: activity.venue_name || 'Unknown Venue',
      sport_venue_name: activity.sport_venue_name || 'Unknown Sport Venue',
      start_time: activity.start_time || '',
      end_time: activity.end_time || '',
      status: activity.status || 'unknown'
    })),
    recommendedVenues: data.recommended_venues.map(venue => ({
      id: venue.id,
      name: venue.name,
      sportVenueName: venue.sport_venue_name
    }))
  };
};

export const getUserDashboardData = async () => {
  console.log("getUserDashboardData called");
  try {
    if (USE_MOCK_DATA) {
      // 使用模拟数据
      await delay(500); // 模拟网络延迟
      console.log("Returning mock data:", mockDashboardData);
      return mockDashboardData;
    } else {
      // 使用真实 API
      const response = await userApi.get('/dashboard');
      console.log("API response:", response);
      return transformDashboardData(response.data);
    }
  } catch (error) {
    console.error("Error in getUserDashboardData:", error);
    if (error.response) {
      // 服务器响应了，但状态码不在 2xx 范围内
      console.error("Error response:", error.response.data);
      throw new Error(error.response.data.message || "An error occurred while fetching dashboard data");
    } else if (error.request) {
      // 请求已经发出，但没有收到响应
      console.error("No response received");
      throw new Error("No response received from server");
    } else {
      // 在设置请求时发生了错误
      console.error("Error", error.message);
      throw new Error("An error occurred while setting up the request");
    }
  }
};

// 其他用户相关的服务函数可以在这里添加
export const updateUserProfile = async (userData) => {
  // 实现更新用户资料的逻辑
};

export const changeUserPassword = async (oldPassword, newPassword) => {
  // 实现更改用户密码的逻辑
};