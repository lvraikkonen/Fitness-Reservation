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

// 配置标志：是否使用模拟头像数据
const USE_MOCK_AVATAR = true;

// 从 localStorage 获取头像 URL
const getAvatarFromStorage = () => {
  return localStorage.getItem('mockAvatarUrl') || "";
};

// 将头像 URL 保存到 localStorage
const saveAvatarToStorage = (avatarUrl) => {
  localStorage.setItem('mockAvatarUrl', avatarUrl);
};

export const getCurrentUserProfile = async () => {
  try {
    const response = await userApi.get('/me');
    const userData = response.data;

    // 如果使用模拟头像，替换 API 返回的头像 URL
    if (USE_MOCK_AVATAR) {
      userData.avatar_url = getAvatarFromStorage();
    }

    return userData;
  } catch (error) {
    console.error("Error in getCurrentUserProfile:", error);
    handleApiError(error, "Failed to fetch current user profile");
  }
};

export const updateUserProfile = async (userData) => {
  try {
    const response = await userApi.put('/me', userData);
    const updatedUserData = response.data;

    // 如果使用模拟头像，保持使用存储的头像 URL
    if (USE_MOCK_AVATAR) {
      updatedUserData.avatar_url = getAvatarFromStorage();
    }

    return updatedUserData;
  } catch (error) {
    console.error("Error in updateUserProfile:", error);
    handleApiError(error, "Failed to update user profile");
  }
};

export const uploadUserAvatar = async (file) => {
  if (USE_MOCK_AVATAR) {
    // 模拟头像上传
    await new Promise(resolve => setTimeout(resolve, 1000)); // 模拟网络延迟

    let avatarUrl;
    if (typeof file === 'string' && file.startsWith('data:')) {
      // 如果文件已经是 base64 字符串，直接使用
      avatarUrl = file;
    } else if (file instanceof Blob) {
      // 如果是 Blob 或 File 对象，使用 FileReader 读取
      avatarUrl = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (error) => reject(error);
        reader.readAsDataURL(file);
      });
    } else {
      throw new Error('Invalid file type for avatar upload');
    }

    saveAvatarToStorage(avatarUrl);
    return {
      avatar_url: avatarUrl,
      message: "Avatar uploaded successfully"
    };
  } else {
    // 真实的头像上传 API 调用
    try {
      const formData = new FormData();
      formData.append('avatar', file);
      const response = await userApi.post('/me/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error("Error in uploadUserAvatar:", error);
      handleApiError(error, "Failed to upload avatar");
    }
  }
};

// 配置标志：是否使用模拟设置数据
const USE_MOCK_SETTINGS = true;

// 从 localStorage 获取设置
const getSettingsFromStorage = () => {
  const storedSettings = localStorage.getItem('mockUserSettings');
  return storedSettings ? JSON.parse(storedSettings) : {
    email_notifications: true,
    sms_notifications: false,
    dark_mode: false
  };
};

// 将设置保存到 localStorage
const saveSettingsToStorage = (settings) => {
  localStorage.setItem('mockUserSettings', JSON.stringify(settings));
};

export const getUserSettings = async () => {
  if (USE_MOCK_SETTINGS) {
    // 模拟 API 延迟
    await new Promise(resolve => setTimeout(resolve, 500));
    return getSettingsFromStorage();
  } else {
    try {
      const response = await userApi.get('/me/settings');
      return response.data;
    } catch (error) {
      console.error("Error in getUserSettings:", error);
      handleApiError(error, "Failed to fetch user settings");
    }
  }
};

export const updateUserSettings = async (settings) => {
  if (USE_MOCK_SETTINGS) {
    // 模拟 API 延迟
    await new Promise(resolve => setTimeout(resolve, 500));
    saveSettingsToStorage(settings);
    return settings;
  } else {
    try {
      const response = await userApi.put('/me/settings', settings);
      return response.data;
    } catch (error) {
      console.error("Error in updateUserSettings:", error);
      handleApiError(error, "Failed to update user settings");
    }
  }
};

export const fetchUserActivity = async (userId) => {
  try {
    const response = await userApi.get(`/users/${userId}/activity`);
    return response.data;
  } catch (error) {
    console.error("Error in fetchUserActivity:", error);
    handleApiError(error, "Failed to fetch user activity");
  }
};

// 错误处理辅助函数
const handleApiError = (error, defaultMessage) => {
  if (error.response) {
    throw new Error(error.response.data.message || defaultMessage);
  } else if (error.request) {
    throw new Error("No response received from server");
  } else {
    throw new Error(defaultMessage);
  }
};