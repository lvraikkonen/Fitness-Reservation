import dayjs from 'dayjs';
import advancedFormat from 'dayjs/plugin/advancedFormat';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import localeData from 'dayjs/plugin/localeData';
import weekday from 'dayjs/plugin/weekday';
import weekOfYear from 'dayjs/plugin/weekOfYear';
import weekYear from 'dayjs/plugin/weekYear';

import { ConfigProvider } from 'antd';
import zhCN from 'antd/lib/locale/zh_CN';

import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Venues from './pages/Venues';
import Reservations from './pages/Reservations';
import UpcomingReservations from './pages/UpcomingReservations';
import ReservationDetails from './pages/ReservationDetails';
import RecentActivities from './pages/RecentActivities';
import Feedback from './pages/Feedback';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import PrivateRoute from './components/PrivateRoute';
import AdminRoute from './components/AdminRoute';
import MainLayout from './components/MainLayout';
import AdminLayout from './components/AdminLayout';
import NotFound from './pages/NotFound';

// 新增管理员页面
import AdminDashboard from './pages/admin/AdminDashboard';
import VenueManagement from './pages/admin/VenueManagement';
import UserManagement from './pages/admin/UserManagement';
import ReservationManagement from './pages/admin/ReservationManagement';

import './styles/darkMode.css';  // 导入 Dark Mode 样式

const { Content } = Layout;

dayjs.extend(advancedFormat);
dayjs.extend(customParseFormat);
dayjs.extend(localeData);
dayjs.extend(weekday);
dayjs.extend(weekOfYear);
dayjs.extend(weekYear);

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>  {/* 添加 ThemeProvider */}
        <ConfigProvider locale={zhCN}>
          <Router>
            <Layout style={{ minHeight: '100vh' }}>
              <Content style={{ padding: '0 50px' }}>
                <Routes>
                  <Route path="/" element={<Login />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />

                  {/* 普通用户路由 */}
                  <Route element={<PrivateRoute><MainLayout /></PrivateRoute>}>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/venues" element={<Venues />} />
                    <Route path="/venues/:id" element={<Venues />} />
                    <Route path="/reservations" element={<Reservations />} />
                    <Route path="/upcoming-reservations" element={<UpcomingReservations />} />
                    <Route path="/reservations/:id" element={<ReservationDetails />} />
                    <Route path="/recent-activities" element={<RecentActivities />} />
                    <Route path="/feedback" element={<Feedback />} />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="/settings" element={<Settings />} />
                  </Route>

                  {/* 管理员路由 */}
                  <Route path="/admin" element={<AdminRoute><AdminLayout /></AdminRoute>}>
                    <Route index element={<Navigate to="dashboard" replace />} />
                    <Route path="dashboard" element={<AdminDashboard />} />
                    <Route path="venues" element={<VenueManagement />} />
                    <Route path="users" element={<UserManagement />} />
                    <Route path="reservations" element={<ReservationManagement />} />
                  </Route>

                  {/* 404 页面 */}
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </Content>
            </Layout>
          </Router>
        </ConfigProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;