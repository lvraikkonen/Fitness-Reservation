import React from 'react';
import { Card, Tag, Space, Button } from 'antd';
import { CalendarOutlined, ClockCircleOutlined, EnvironmentOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';

const getStatusColor = (status) => {
  switch(status.toLowerCase()) {
    case 'pending': return 'blue';
    case 'confirmed': return 'green';
    case 'cancelled': return 'red';
    default: return 'default';
  }
};

const ReservationCard = ({ reservation, onCancel }) => {
  return (
    <Card
      title={
        <Space>
          <EnvironmentOutlined />
          {reservation.sport_venue_name} - {reservation.venue_name}
        </Space>
      }
      extra={
        <Tag color={getStatusColor(reservation.status)}>
          {reservation.status.toUpperCase()}
        </Tag>
      }
      style={{ marginBottom: 16 }}
    >
      <p>
        <CalendarOutlined /> Date: {reservation.date}
      </p>
      <p>
        <ClockCircleOutlined /> Time: {reservation.start_time} - {reservation.end_time}
      </p>
      <Space>
        <Link to={`/reservations/${reservation.id}`}>
          <Button type="primary">View Details</Button>
        </Link>
        {reservation.status !== 'cancelled' && (
          <Button onClick={() => onCancel(reservation.id)} danger>
            Cancel
          </Button>
        )}
      </Space>
    </Card>
  );
};

export default ReservationCard;