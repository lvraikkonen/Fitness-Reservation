import React, { useState, useEffect } from 'react';
import { Row, Col, Space, Button, DatePicker, Select, message, Spin, Pagination } from 'antd';
import { fetchVenues, fetchUserReservations, cancelReservation } from '../services/reservationService';
import ReservationCard from '../components/ReservationCard';

const { RangePicker } = DatePicker;
const { Option } = Select;

const UpcomingReservationsPage = () => {
  const [venues, setVenues] = useState([]);
  const [selectedVenue, setSelectedVenue] = useState(null);
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState(null);

  const [totalReservations, setTotalReservations] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  useEffect(() => {
    loadVenues();
  }, []);

  useEffect(() => {
    if (selectedVenue) {
      loadUserReservations();
    }
  }, [selectedVenue, dateRange, currentPage]);

  const loadVenues = async () => {
    setLoading(true);
    try {
      const data = await fetchVenues();
      setVenues(data);
      if (data.length > 0) {
        setSelectedVenue(data[0].id);
      }
    } catch (error) {
      message.error('Failed to load venues');
    } finally {
      setLoading(false);
    }
  };

  const loadUserReservations = async () => {
    setLoading(true);
    try {
      const data = await fetchUserReservations(selectedVenue, currentPage, pageSize, dateRange);
      setReservations(data.reservations);
      setTotalReservations(data.total_count);
    } catch (error) {
      message.error('Failed to load reservations');
    } finally {
      setLoading(false);
    }
  };

  const handleVenueChange = (venueId) => {
    setSelectedVenue(venueId);
    setCurrentPage(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleCancelReservation = (reservationId) => {
    message.confirm({
      title: 'Are you sure you want to cancel this reservation?',
      content: 'This action cannot be undone.',
      onOk: async () => {
        try {
          await cancelReservation(reservationId);
          message.success('Reservation cancelled successfully');
          loadUserReservations();
        } catch (error) {
          message.error('Failed to cancel reservation');
        }
      },
    });
  };

  return (
    <Spin spinning={loading}>
      <h1>Upcoming Reservations</h1>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Space>
            <Select
              style={{ width: 200 }}
              placeholder="Select a venue"
              onChange={handleVenueChange}
              value={selectedVenue}
            >
              {venues.map(venue => (
                <Option key={venue.id} value={venue.id}>{venue.name}</Option>
              ))}
            </Select>
            <RangePicker onChange={(dates) => {
              setDateRange(dates);
              setCurrentPage(1);
            }} />
            <Button onClick={loadUserReservations} type="primary">
              Apply Filters
            </Button>
          </Space>
        </Col>
        <Col span={24}>
          {reservations.map(reservation => (
            <ReservationCard
              key={reservation.id}
              reservation={reservation}
              onCancel={handleCancelReservation}
            />
          ))}
        </Col>
        <Col span={24}>
          <Pagination
            current={currentPage}
            total={totalReservations}
            pageSize={pageSize}
            onChange={handlePageChange}
            showSizeChanger={false}
            showTotal={(total, range) => `${range[0]}-${range[1]} of ${total} reservations`}
          />
        </Col>
      </Row>
    </Spin>
  );
};

export default UpcomingReservationsPage;