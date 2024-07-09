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
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { Layout } from 'antd';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
// import VenueManagement from './pages/VenueManagement';
import Reservations from './pages/Reservations';
// import Statistics from './pages/Statistics';
import Feedback from './pages/Feedback';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import PrivateRoute from './components/PrivateRoute';

const { Content } = Layout;

dayjs.extend(advancedFormat);
dayjs.extend(customParseFormat);
dayjs.extend(localeData);
dayjs.extend(weekday);
dayjs.extend(weekOfYear);
dayjs.extend(weekYear);

function App() {
  return (
    <ConfigProvider locale={zhCN}>
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Content style={{ padding: '0 50px' }}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="/reservations" element={<PrivateRoute><Reservations /></PrivateRoute>} />
            {/* <Route path="/venues" element={<PrivateRoute><VenueManagement /></PrivateRoute>} />
            <Route path="/statistics" element={<PrivateRoute><Statistics /></PrivateRoute>} /> */}
            <Route path="/feedback" element={<PrivateRoute><Feedback /></PrivateRoute>} />
            <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
            <Route path="/settings" element={<PrivateRoute><Settings /></PrivateRoute>} />
          </Routes>
        </Content>
      </Layout>
    </Router>
    </ConfigProvider>
  );
}

export default App;