import React, { useState, useEffect } from 'react';
import { Table, Button, message, Tag, Space, Modal } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { getAllReservations, createReservation, cancelReservation, confirmReservation } from '../../services/reservationService';

const { confirm } = Modal;

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

  const handleStatusChange = async (id, newStatus) => {
    if (newStatus === 'confirmed') {
      confirm({
        title: 'Are you sure you want to confirm this reservation?',
        icon: <ExclamationCircleOutlined />,
        content: 'This action cannot be undone.',
        onOk: async () => {
          try {
            await confirmReservation(id);
            message.success('Reservation confirmed successfully');
            // 刷新预约列表
            fetchReservations();
          } catch (error) {
            message.error('Failed to confirm reservation: ' + error.message);
          }
        },
        onCancel() {
          console.log('Confirmation cancelled');
        },
      });
    } else if (newStatus === 'cancelled') {
      confirm({
        title: 'Are you sure you want to cancel this reservation?',
        icon: <ExclamationCircleOutlined />,
        content: 'This action cannot be undone.',
        onOk: async () => {
          try {
            await cancelReservation(id);
            message.success('Reservation cancelled successfully');
            // 刷新预约列表
            fetchReservations();
          } catch (error) {
            message.error('Failed to cancel reservation: ' + error.message);
          }
        },
        onCancel() {
          console.log('Cancellation cancelled');
        },
      });
    } else {
      console.log(`Status change to ${newStatus} is not implemented yet`);
    }
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
      { title: 'User Name', dataIndex: 'user_name', key: 'user_name' },
      { title: 'Date', dataIndex: 'date', key: 'date' },
      { 
        title: 'Start Time', 
        dataIndex: 'venue_available_time_slot_start', 
        key: 'venue_available_time_slot_start' 
      },
      { 
        title: 'End Time', 
        dataIndex: 'venue_available_time_slot_end', 
        key: 'venue_available_time_slot_end' 
      },
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