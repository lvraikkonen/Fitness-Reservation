import React, { useState, useEffect } from 'react';
import { Row, Col, Card, List, Statistic, Button, Calendar, Spin, Typography, Tag, Tooltip } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import { CalendarOutlined, HistoryOutlined, PlusOutlined, CheckCircleOutlined, CloseCircleOutlined, FieldTimeOutlined } from '@ant-design/icons';
import { getUserDashboardData } from '../services/userService';
import { useAuth } from '../contexts/AuthContext';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { Text } = Typography;

const ActivityIcon = ({ type }) => {
  switch (type) {
    case 'reservation_created':
      return <CalendarOutlined style={{ color: '#1890ff' }} />;
    case 'reservation_cancelled':
      return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
    case 'reservation_checked_in':
      return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
    default:
      return <FieldTimeOutlined style={{ color: '#faad14' }} />;
  }
};

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();  // 使用 AuthContext 获取用户信息
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const data = await getUserDashboardData();
        console.log("Fetched dashboard data:", data);
        setDashboardData(data);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  const handleNavigation = (path) => {
    navigate(path, { state: { from: 'dashboard' } });
  };

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
          <Card title="Upcoming Reservations" extra={<Link to="/upcoming-reservations">View All</Link>}>
            <List
              dataSource={dashboardData.upcomingReservations.slice(0, 5)}
              renderItem={item => (
                <List.Item
                  actions={[<a onClick={() => handleNavigation(`/reservations/${item.id}`)}>View Details</a>]}
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
            <Button type="primary" icon={<PlusOutlined />} style={{ marginTop: 16 }} onClick={() => handleNavigation('/reservations')}>
              Quick Reserve
            </Button>
          </Card>
        </Col>
      </Row>
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={12}>
        <Card title="Recent Activities" extra={<a onClick={() => handleNavigation('/activities')}>View All</a>}>
          {console.log("Recent activities:", dashboardData.recentActivities)}
          {Array.isArray(dashboardData.recentActivities) && dashboardData.recentActivities.length > 0 ? (
              <List
                itemLayout="horizontal"
                dataSource={dashboardData.recentActivities}
                renderItem={(item) => {
                  return (
                    <List.Item key={item.id}>
                      <List.Item.Meta
                        avatar={<ActivityIcon type={item.activity_type} />}
                        title={
                          <Text>
                            {item.activity_type === 'reservation_created'
                              ? 'Created reservation for '
                              : item.activity_type === 'reservation_cancelled'
                              ? 'Cancelled reservation for '
                              : 'Checked in at '}
                            <Text strong>{item.venue_name}</Text> at <Text strong>{item.sport_venue_name}</Text>
                          </Text>
                        }
                        description={
                          <>
                            <Tooltip title={dayjs(item.activity_timestamp).format('YYYY-MM-DD HH:mm:ss')}>
                              <Text type="secondary">{dayjs(item.activity_timestamp).fromNow()}</Text>
                            </Tooltip>
                            <br />
                            <Text type="secondary">
                              {dayjs(item.date).format('MMMM D, YYYY')} {item.start_time} - {item.end_time}
                            </Text>
                          </>
                        }
                      />
                    </List.Item>
                  );
                }}
              />
            ) : (
              <Text>No recent activities</Text>
            )}
          </Card>
        </Col>

        <Col span={12}>
          <Card title="Recommended Venues" extra={<a onClick={() => handleNavigation('/venues')}>Explore More</a>}>
            <List
              dataSource={dashboardData.recommendedVenues}
              renderItem={item => (
                <List.Item
                  actions={[<a onClick={() => handleNavigation(`/venues/${item.id}`)}>Book Now</a>]}
                >
                  <List.Item.Meta
                    title={item.name}
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