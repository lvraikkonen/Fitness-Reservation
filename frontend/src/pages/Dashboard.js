import React from 'react';
import { Typography, Spin } from 'antd';
import MainLayout from '../components/MainLayout';
import StatisticsSummary from '../components/StatisticsSummary';
import { useAuth } from '../contexts/AuthContext';

const { Title } = Typography;

const Dashboard = () => {
  const { user } = useAuth();

  if (!user) {
    return (
      <MainLayout>
        <Spin size="large" />
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <Title level={2}>Welcome, {user.full_name || user.username}!</Title>
      {/* <RecentReservations /> */}
      <StatisticsSummary />
    </MainLayout>
  );
};

export default Dashboard;