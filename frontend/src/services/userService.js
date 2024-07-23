// services/userService.js

// 模拟API调用延迟
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// MockData
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

export const getUserDashboardData = async () => {
  console.log("getUserDashboardData called");
  try {
    // 如果使用真实 API
    // const response = await api.get('/user/dashboard');
    // console.log("API response:", response);
    // return response.data;

    // 如果使用 mock 数据
    await delay(500);
    console.log("Returning mock data:", mockDashboardData);
    return mockDashboardData;
  } catch (error) {
    console.error("Error in getUserDashboardData:", error);
    throw error;
  }
};

// 其他用户相关的服务函数可以在这里添加
export const updateUserProfile = async (userData) => {
  // 实现更新用户资料的逻辑
};

export const changeUserPassword = async (oldPassword, newPassword) => {
  // 实现更改用户密码的逻辑
};