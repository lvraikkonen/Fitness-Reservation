import React, { useState, useMemo } from 'react';
import { List, Divider, Button, Empty, Spin, Pagination, Tag, Select, DatePicker, Space, Alert } from 'antd';
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

    // Custom sort function
  const customSort = (a, b) => {
    const dateA = dayjs(a.date);
    const dateB = dayjs(b.date);
    const now = dayjs();

    // 首先按照日期排序
    if (dateA.isBefore(dateB)) return -1;
    if (dateA.isAfter(dateB)) return 1;

    // 如果日期相同，按照状态排序
    const statusOrder = ['confirmed', 'pending', 'cancelled'];
    const statusA = statusOrder.indexOf(a.status.toLowerCase());
    const statusB = statusOrder.indexOf(b.status.toLowerCase());
    
    if (statusA !== statusB) return statusA - statusB;

    // 如果状态也相同，按照开始时间排序
    return a.start_time.localeCompare(b.start_time);
  };

  // Sort reservations
  filtered.sort(customSort);

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
        renderItem={(item, index) => {
          const isPast = dayjs(item.date).isBefore(dayjs(), 'day');
          const canCancel = !isPast && item.status.toLowerCase() !== 'cancelled';
          const isUpcoming = dayjs(item.date).isAfter(dayjs(), 'day') && 
                             dayjs(item.date).diff(dayjs(), 'days') <= 3 &&
                             item.status.toLowerCase() !== 'cancelled' &&
                             !item.checked_in_at;
  
          const showDivider = index > 0 && 
                              dayjs(item.date).isAfter(dayjs(), 'day') && 
                              dayjs(sortedAndFilteredReservations[index-1].date).isBefore(dayjs(), 'day');
  
          return (
            <>
              {showDivider && <Divider>Past Reservations</Divider>}
              <List.Item
                actions={[
                  canCancel && (
                    <Button onClick={() => onCancel(item.id)} type="link" danger>
                      Cancel
                    </Button>
                  )
                ].filter(Boolean)}
                style={{
                  opacity: item.status.toLowerCase() === 'cancelled' ? 0.5 : 1,
                  backgroundColor: isPast ? '#f0f0f0' : 'white'
                }}
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
                      {item.checked_in_at && <p>Checked in at: {dayjs(item.checked_in_at).format('YYYY-MM-DD HH:mm')}</p>}
                    </>
                  }
                />
              </List.Item>
            </>
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