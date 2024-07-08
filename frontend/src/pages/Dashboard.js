import React from 'react';
import { Typography } from 'antd';
import MainLayout from '../components/MainLayout';
import StatisticsSummary from '../components/StatisticsSummary';

const { Title } = Typography;

const Dashboard = () => {
  return (
    <MainLayout>
      <Title level={2}>Welcome to the Dashboard</Title>
      {/* <RecentReservations /> */}
      <StatisticsSummary />
    </MainLayout>
  );
};

export default Dashboard;