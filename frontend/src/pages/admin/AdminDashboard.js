import React from 'react';
import { Card, Row, Col, Statistic } from 'antd';
import { UserOutlined, EnvironmentOutlined, CalendarOutlined } from '@ant-design/icons';

const AdminDashboard = () => {
  return (
    <div>
      <h2>Admin Dashboard</h2>
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Total Users"
              value={1128}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Total Venues"
              value={93}
              prefix={<EnvironmentOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Today's Reservations"
              value={11}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AdminDashboard;