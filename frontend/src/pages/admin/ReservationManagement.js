import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, message } from 'antd';
import { reservationApi } from '../../services/api';

const ReservationManagement = () => {
  const [reservations, setReservations] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedReservation, setSelectedReservation] = useState(null);

  useEffect(() => {
    fetchReservations();
  }, []);

  const fetchReservations = async () => {
    try {
      const response = await reservationApi.get('/');
      setReservations(response.data);
    } catch (error) {
      message.error('Failed to fetch reservations');
    }
  };

  const showModal = (reservation) => {
    setSelectedReservation(reservation);
    setIsModalVisible(true);
  };

  const handleCancel = async () => {
    try {
      await reservationApi.put(`/${selectedReservation.id}`, { status: 'cancelled' });
      message.success('Reservation cancelled successfully');
      setIsModalVisible(false);
      fetchReservations();
    } catch (error) {
      message.error('Failed to cancel reservation');
    }
  };

  const columns = [
    { title: 'User', dataIndex: ['user', 'username'], key: 'user' },
    { title: 'Venue', dataIndex: ['venue', 'name'], key: 'venue' },
    { title: 'Date', dataIndex: 'date', key: 'date' },
    { title: 'Start Time', dataIndex: 'start_time', key: 'start_time' },
    { title: 'End Time', dataIndex: 'end_time', key: 'end_time' },
    { title: 'Status', dataIndex: 'status', key: 'status' },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Button onClick={() => showModal(record)} disabled={record.status === 'cancelled'}>
          Cancel
        </Button>
      ),
    },
  ];

  return (
    <div>
      <h2>Reservation Management</h2>
      <Table columns={columns} dataSource={reservations} rowKey="id" />
      <Modal
        title="Cancel Reservation"
        visible={isModalVisible}
        onOk={handleCancel}
        onCancel={() => setIsModalVisible(false)}
      >
        <p>Are you sure you want to cancel this reservation?</p>
      </Modal>
    </div>
  );
};

export default ReservationManagement;