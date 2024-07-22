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
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Reservations from './pages/Reservations';
import Feedback from './pages/Feedback';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import PrivateRoute from './components/PrivateRoute';
import AdminRoute from './components/AdminRoute';
import AdminLayout from './components/AdminLayout';
import NotFound from './pages/NotFound';

// 新增管理员页面
import AdminDashboard from './pages/admin/AdminDashboard';
import VenueManagement from './pages/admin/VenueManagement';
import UserManagement from './pages/admin/UserManagement';
import ReservationManagement from './pages/admin/ReservationManagement';

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
      <ConfigProvider locale={zhCN}>
        <Router>
          <Layout style={{ minHeight: '100vh' }}>
            <Content style={{ padding: '0 50px' }}>
              <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
                <Route path="/reservations" element={<PrivateRoute><Reservations /></PrivateRoute>} />
                <Route path="/feedback" element={<PrivateRoute><Feedback /></PrivateRoute>} />
                <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
                <Route path="/settings" element={<PrivateRoute><Settings /></PrivateRoute>} />
                
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
    </AuthProvider>
  );
}

export default App;