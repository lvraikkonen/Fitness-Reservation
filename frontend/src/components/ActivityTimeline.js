import React from 'react';
import { Timeline, Card, Typography, Tag, Tooltip } from 'antd';
import { CalendarOutlined, ClockCircleOutlined, EnvironmentOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
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
      return <ClockCircleOutlined style={{ color: '#faad14' }} />;
  }
};

const getStatusColor = (status) => {
  switch(status.toLowerCase()) {
    case 'pending': return 'blue';
    case 'confirmed': return 'green';
    case 'cancelled': return 'red';
    default: return 'default';
  }
};

const ActivityTimeline = ({ activities }) => {
  return (
    <Timeline mode="left">
      {activities.map((activity) => (
        <Timeline.Item
          key={activity.id}
          dot={<ActivityIcon type={activity.activity_type} />}
        >
          <Card style={{ marginBottom: 16 }}>
            <Text strong>
              {activity.activity_type === 'reservation_created'
                ? 'Created reservation for '
                : activity.activity_type === 'reservation_cancelled'
                ? 'Cancelled reservation for '
                : 'Checked in at '}
              <Text type="secondary">{activity.venue_name}</Text>
            </Text>
            <br />
            <Text>
              <EnvironmentOutlined /> {activity.sport_venue_name}
            </Text>
            <br />
            <Text>
              <CalendarOutlined /> {activity.date}
            </Text>
            <br />
            <Text>
              <ClockCircleOutlined /> {activity.start_time} - {activity.end_time}
            </Text>
            <br />
            <Tooltip title={activity.timestamp}>
              <Tag color="blue">{dayjs(activity.timestamp).fromNow()}</Tag>
            </Tooltip>
            <Tag color={getStatusColor(activity.status)}>
              {activity.status.charAt(0).toUpperCase() + activity.status.slice(1)}
            </Tag>
          </Card>
        </Timeline.Item>
      ))}
    </Timeline>
  );
};

export default ActivityTimeline;