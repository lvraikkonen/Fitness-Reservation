import React, { useState, useEffect } from 'react';
import { Row, Col, Card, List, Statistic, Button, Calendar, Spin } from 'antd';
import { Link } from 'react-router-dom';
import { CalendarOutlined, HistoryOutlined, PlusOutlined } from '@ant-design/icons';
import { getUserDashboardData } from '../services/userService';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();  // 使用 AuthContext 获取用户信息

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const data = await getUserDashboardData();
        setDashboardData(data);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) {
    return <Spin size="large" />;
  }

  if (!dashboardData) {
    return <div>Error loading dashboard data. Please try again later.</div>;
  }

  return (
    <div>
      <h1>Hello, {user?.username || 'User'}!</h1>
      <Row gutter={[16, 16]}>
        <Col span={16}>
          <Card title="Upcoming Reservations" extra={<Link to="/reservations">View All</Link>}>
            <List
              dataSource={dashboardData.upcomingReservations}
              renderItem={item => (
                <List.Item
                  actions={[<Link to={`/reservations/${item.id}`}>View Details</Link>]}
                >
                  <List.Item.Meta
                    avatar={<CalendarOutlined />}
                    title={item.venueName}
                    description={`${item.date} ${item.startTime} - ${item.endTime}`}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="This Month's Reservations"
              value={dashboardData.monthlyReservationCount}
              suffix={`/ ${dashboardData.monthlyReservationLimit}`}
            />
            <Button type="primary" icon={<PlusOutlined />} style={{ marginTop: 16 }}>
              <Link to="/venues">Quick Reserve</Link>
            </Button>
          </Card>
        </Col>
      </Row>
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="Recent Activities" extra={<Link to="/activities">View All</Link>}>
            <List
              dataSource={dashboardData.recentActivities}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<HistoryOutlined />}
                    title={item.action}
                    description={item.date}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Recommended Venues" extra={<Link to="/venues">Explore More</Link>}>
            <List
              dataSource={dashboardData.recommendedVenues}
              renderItem={item => (
                <List.Item
                  actions={[<Link to={`/venues/${item.id}`}>Book Now</Link>]}
                >
                  <List.Item.Meta
                    title={item.name}
                    description={`Popular time: ${item.popularTime}`}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
      <Row style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="Reservation Calendar">
            <Calendar
              fullscreen={false}
              dateCellRender={(date) => {
                const reservationsForDate = dashboardData.upcomingReservations.filter(
                  res => res.date === date.format('YYYY-MM-DD')
                );
                return reservationsForDate.length ? (
                  <div className="calendar-reservation-indicator">{reservationsForDate.length}</div>
                ) : null;
              }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;