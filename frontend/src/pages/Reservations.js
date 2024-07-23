import React, { useState, useEffect, useRef } from 'react';
import { Row, Col, Select, message, Spin, Modal } from 'antd';
import VenueCalendar from '../components/VenueCalendar';
import ReservationForm from '../components/ReservationForm';
import ReservationList from '../components/ReservationList';
import { fetchVenues, fetchUserReservations, createReservation, cancelReservation } from '../services/reservationService';

const { Option } = Select;
const { confirm } = Modal;

const Reservations = () => {
  const [venues, setVenues] = useState([]);
  const [selectedVenue, setSelectedVenue] = useState(null);
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(false);

  const [totalReservations, setTotalReservations] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const calendarRef = useRef(null);

  useEffect(() => {
    loadVenues();
  }, []);

  useEffect(() => {
    if (selectedVenue) {
      loadUserReservations();
    }
  }, [selectedVenue]);

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

  const loadUserReservations = async (page = 1) => {
    setLoading(true);
    try {
      const data = await fetchUserReservations(selectedVenue, page, pageSize);
      setReservations(data.reservations);
      setTotalReservations(data.total_count);
      setCurrentPage(data.page);
      setPageSize(data.page_size);
    } catch (error) {
      message.error('Failed to load reservations');
    } finally {
      setLoading(false);
    }
  };

  const handleVenueChange = (venueId) => {
    setSelectedVenue(venueId);
  };

  const handlePageChange = (page) => {
    loadUserReservations(page);
  };

  const handleCreateReservation = async (reservationData) => {
    try {
      await createReservation(selectedVenue, reservationData);
      message.success('Reservation created successfully');
      loadUserReservations();
      if (calendarRef.current) {
        calendarRef.current.refreshCalendar();
      }
    } catch (error) {
      message.error('Failed to create reservation');
    }
  };

  const handleCancelReservation = (reservationId) => {
    confirm({
      title: 'Are you sure you want to cancel this reservation?',
      content: 'This action cannot be undone.',
      onOk: async () => {
        try {
          await cancelReservation(reservationId);
          message.success('Reservation cancelled successfully');
          loadUserReservations();
          if (calendarRef.current) {
            calendarRef.current.refreshCalendar();
          }
        } catch (error) {
          message.error('Failed to cancel reservation');
        }
      },
    });
  };

  return (
    <Spin spinning={loading}>
        <div>
          <h1>Venue Reservations</h1>
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Select
                style={{ width: 200 }}
                placeholder="Select a venue"
                onChange={handleVenueChange}
                value={selectedVenue}
                loading={loading}
              >
                {venues.map(venue => (
                  <Option key={venue.id} value={venue.id}>{venue.name}</Option>
                ))}
              </Select>
            </Col>
            {selectedVenue && (
              <>
                <Col span={24} style={{ height: 'calc(70% - 32px)'}}>
                  <VenueCalendar 
                    venueId={selectedVenue} 
                    ref={calendarRef}
                  />
                </Col>
                <Col span={24}>
                  <ReservationForm onSubmit={handleCreateReservation} />
                </Col>
                <Col span={24}>
                  <ReservationList 
                    reservations={reservations}
                    onCancel={handleCancelReservation}
                    loading={loading}
                    total={totalReservations}
                    current={currentPage}
                    pageSize={pageSize}
                    onPageChange={handlePageChange}
                  />
                </Col>
              </>
            )}
          </Row>
        </div>
      </Spin>
  );
};

export default Reservations;