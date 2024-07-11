import React, { useState, useMemo } from 'react';
import { List, Button, Empty, Spin, Pagination, Tag, Select, DatePicker, Space, Alert } from 'antd';
import dayjs from 'dayjs';

const { Option } = Select;

const ReservationList = ({ 
  reservations, 
  onCancel, 
  loading, 
  total, 
  current, 
  pageSize, 
  onPageChange 
}) => {
  const [sortBy, setSortBy] = useState('date');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterDate, setFilterDate] = useState(null);

  const getStatusColor = (status) => {
    switch(status.toLowerCase()) {
      case 'pending': return 'blue';
      case 'confirmed': return 'green';
      case 'cancelled': return 'red';
      default: return 'default';
    }
  };

  const sortedAndFilteredReservations = useMemo(() => {
    let filtered = [...reservations];

    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(item => item.status.toLowerCase() === filterStatus);
    }

    // Apply date filter
    if (filterDate) {
      filtered = filtered.filter(item => dayjs(item.date).isSame(filterDate, 'day'));
    }

    // Sort reservations
    filtered.sort((a, b) => {
      if (sortBy === 'date') {
        return dayjs(a.date).diff(dayjs(b.date));
      } else if (sortBy === 'status') {
        return a.status.localeCompare(b.status);
      }
      return 0;
    });

    return filtered;
  }, [reservations, sortBy, filterStatus, filterDate]);

  if (loading) {
    return <Spin tip="Loading reservations..." />;
  }

  if (!reservations || reservations.length === 0) {
    return <Empty description="No reservations found" />;
  }

  return (
    <>
      <Space style={{ marginBottom: 16 }}>
        <Select defaultValue="date" style={{ width: 120 }} onChange={setSortBy}>
          <Option value="date">Sort by Date</Option>
          <Option value="status">Sort by Status</Option>
        </Select>
        <Select defaultValue="all" style={{ width: 120 }} onChange={setFilterStatus}>
          <Option value="all">All Statuses</Option>
          <Option value="pending">Pending</Option>
          <Option value="confirmed">Confirmed</Option>
          <Option value="cancelled">Cancelled</Option>
        </Select>
        <DatePicker onChange={(date) => setFilterDate(date)} />
      </Space>

      <List
        header={<div>My Reservations</div>}
        bordered
        dataSource={sortedAndFilteredReservations}
        renderItem={item => {
          const isPast = dayjs(item.date).isBefore(dayjs(), 'day');
          const canCancel = !isPast && item.status.toLowerCase() !== 'cancelled';
          const isUpcoming = dayjs(item.date).isAfter(dayjs(), 'day') && dayjs(item.date).diff(dayjs(), 'days') <= 3;

          return (
            <List.Item
              actions={[
                canCancel && (
                  <Button onClick={() => onCancel(item.id)} type="link" danger>
                    Cancel
                  </Button>
                )
              ].filter(Boolean)}
              style={item.status.toLowerCase() === 'cancelled' ? { opacity: 0.5 } : {}}
            >
              {isUpcoming && (
                <Alert
                  message="Upcoming Reservation"
                  type="warning"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
              )}
              <List.Item.Meta
                title={
                  <>
                    <span>{`Reservation for ${dayjs(item.date).format('YYYY-MM-DD')}`}</span>
                    <Tag color={getStatusColor(item.status)} style={{ marginLeft: '10px' }}>
                      {item.status}
                    </Tag>
                  </>
                }
                description={
                  <>
                    <p>Time: {item.start_time} - {item.end_time}</p>
                    <p>Venue: {item.sport_venue_name} - {item.venue_name}</p>
                  </>
                }
              />
            </List.Item>
          );
        }}
      />
      <Pagination
        total={total}
        current={current}
        pageSize={pageSize}
        onChange={onPageChange}
        showSizeChanger={false}
        style={{ marginTop: '16px', textAlign: 'right' }}
      />
    </>
  );
};

export default ReservationList;