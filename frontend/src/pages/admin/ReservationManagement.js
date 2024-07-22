import React, { useState, useEffect } from 'react';
import { Table, Button, message, Tag, Space } from 'antd';
import { getAllReservations, createReservation, cancelReservation } from '../../services/reservationService';

const ReservationManagement = () => {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  useEffect(() => {
    fetchReservations();
  }, []);

  const fetchReservations = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      const data = await getAllReservations(page, pageSize);
      setReservations(data.reservations);
      setPagination({
        current: data.page,
        pageSize: data.page_size,
        total: data.total_count
      });
    } catch (error) {
      message.error('Failed to fetch reservations');
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (pagination) => {
    fetchReservations(pagination.current, pagination.pageSize);
  };

  // 占位符函数，将来实现状态更改功能
  const handleStatusChange = async (id, newStatus) => {
    console.log(`Status change requested for reservation ${id} to ${newStatus}`);
    // 将来在这里实现状态更改逻辑
  };

  // 占位符函数，将来实现删除功能
  const handleDelete = async (id) => {
    console.log(`Delete requested for reservation ${id}`);
    // 将来在这里实现删除逻辑
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed':
        return 'green';
      case 'pending':
        return 'gold';
      case 'cancelled':
        return 'red';
      default:
        return 'default';
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'User ID', dataIndex: 'user_id', key: 'user_id' },
    { title: 'Date', dataIndex: 'date', key: 'date' },
    { title: 'Start Time', dataIndex: 'start_time', key: 'start_time' },
    { title: 'End Time', dataIndex: 'end_time', key: 'end_time' },
    { title: 'Sport Venue', dataIndex: 'sport_venue_name', key: 'sport_venue_name' },
    { title: 'Venue', dataIndex: 'venue_name', key: 'venue_name' },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Space>
          {record.status === 'pending' && (
            <Button onClick={() => handleStatusChange(record.id, 'confirmed')} type="primary">
              Confirm
            </Button>
          )}
          {record.status !== 'cancelled' && (
            <Button onClick={() => handleStatusChange(record.id, 'cancelled')} danger>
              Cancel
            </Button>
          )}
          <Button onClick={() => handleDelete(record.id)} danger>
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <h2>Reservation Management</h2>
      <Table 
        columns={columns} 
        dataSource={reservations} 
        rowKey="id" 
        loading={loading}
        pagination={pagination}
        onChange={handleTableChange}
      />
    </div>
  );
};

export default ReservationManagement;