import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Tag, Button, Modal, message, Spin, Space } from 'antd';
import { CalendarOutlined, ClockCircleOutlined, EnvironmentOutlined, UserOutlined } from '@ant-design/icons';
import { fetchReservationDetails, cancelReservation, generateCheckInToken, checkInReservation } from '../services/reservationService';

const { confirm } = Modal;

const getStatusColor = (status) => {
  switch(status.toLowerCase()) {
    case 'pending': return 'blue';
    case 'confirmed': return 'green';
    case 'cancelled': return 'red';
    case 'checked_in': return 'purple';
    default: return 'default';
  }
};

const ReservationDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [reservation, setReservation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReservation();
  }, [id]);

  const fetchReservation = async () => {
    try {
      setLoading(true);
      const data = await fetchReservationDetails(id);
      setReservation(data);
    } catch (error) {
      message.error('Failed to fetch reservation details');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    confirm({
      title: 'Are you sure you want to cancel this reservation?',
      content: 'This action cannot be undone.',
      onOk: async () => {
        try {
          await cancelReservation(id);
          message.success('Reservation cancelled successfully');
          fetchReservation(); // Refresh the reservation data
        } catch (error) {
          message.error('Failed to cancel reservation');
        }
      },
    });
  };

  const handleCheckIn = async () => {
    try {
      let checkInSuccess = false;
      const useToken = true; // 可以根据需求设置
  
      if (useToken) {
        message.loading('Generating check-in token...', 0);
        const token = await generateCheckInToken(id);
        message.destroy();
  
        message.loading('Processing check-in...', 0);
        checkInSuccess = await checkInReservation(null, token);
      } else {
        message.loading('Processing check-in...', 0);
        checkInSuccess = await checkInReservation(id);
      }
  
      message.destroy();
  
      if (checkInSuccess) {
        message.success('Check-in successful');
        await fetchReservation(); // 刷新预约信息
      } else {
        message.warning('Check-in was not successful. Please try again.');
      }
    } catch (error) {
      console.error('Check-in error:', error);
      message.error('Failed to check in: ' + (error.message || 'Unknown error'));
    }
  };

  if (loading) {
    return <Spin size="large" />;
  }

  if (!reservation) {
    return <div>Reservation not found</div>;
  }

  return (
    <Card 
      title="Reservation Details" 
      extra={<Button onClick={() => navigate(-1)}>Back</Button>}
    >
      <Descriptions bordered>
        <Descriptions.Item label="Status" span={3}>
          <Tag color={getStatusColor(reservation.status)}>
            {reservation.status.toUpperCase()}
          </Tag>
        </Descriptions.Item>
        <Descriptions.Item label="Reservation ID">{reservation.id}</Descriptions.Item>
        <Descriptions.Item label="User" span={2}>
          <UserOutlined /> {reservation.userName}
        </Descriptions.Item>
        <Descriptions.Item label="Venue" span={3}>
          <EnvironmentOutlined /> {reservation.sportVenueName} - {reservation.venueName}
        </Descriptions.Item>
        <Descriptions.Item label="Date">
          <CalendarOutlined /> {reservation.date}
        </Descriptions.Item>
        <Descriptions.Item label="Time" span={2}>
          <ClockCircleOutlined /> {reservation.actualStartTime} - {reservation.actualEndTime}
        </Descriptions.Item>
        <Descriptions.Item label="Created At">{reservation.createdAt}</Descriptions.Item>
        <Descriptions.Item label="Updated At" span={2}>{reservation.updatedAt}</Descriptions.Item>
        {reservation.checkedInAt && (
          <Descriptions.Item label="Checked In At" span={3}>{reservation.checkedInAt}</Descriptions.Item>
        )}
        {reservation.cancelledAt && (
          <Descriptions.Item label="Cancelled At" span={3}>{reservation.cancelledAt}</Descriptions.Item>
        )}
      </Descriptions>
      <Space style={{ marginTop: 16 }}>
        {reservation.status === 'confirmed' && (
          <>
            <Button type="primary" onClick={handleCheckIn}>
              Check In
            </Button>
            <Button danger onClick={handleCancel}>
              Cancel Reservation
            </Button>
          </>
        )}
        {reservation.status === 'pending' && (
          <Button danger onClick={handleCancel}>
            Cancel Reservation
          </Button>
        )}
      </Space>
    </Card>
  );
};

export default ReservationDetailsPage;