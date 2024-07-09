// pages/Reservations.js
import React, { useState, useEffect, useRef } from 'react';
import { Row, Col, Select, message } from 'antd';
import MainLayout from '../components/MainLayout';
import VenueCalendar from '../components/VenueCalendar';
import ReservationForm from '../components/ReservationForm';
import ReservationList from '../components/ReservationList';
import { fetchVenues, fetchUserReservations, createReservation, cancelReservation } from '../services/reservationService';

const { Option } = Select;

const Reservations = () => {
  const [venues, setVenues] = useState([]);
  const [selectedVenue, setSelectedVenue] = useState(null);
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(false);

  const calendarRef = useRef(null);
  const listRef = useRef(null);

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

  const loadUserReservations = async () => {
    setLoading(true);
    try {
      const data = await fetchUserReservations(selectedVenue);
      setReservations(data);
    } catch (error) {
      message.error('Failed to load reservations');
    } finally {
      setLoading(false);
    }
  };

  const handleVenueChange = (venueId) => {
    setSelectedVenue(venueId);
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

  const handleCancelReservation = async (reservationId) => {
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
  };

  return (
    <MainLayout>
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
                />
              </Col>
            </>
          )}
        </Row>
      </div>
    </MainLayout>
  );
};

export default Reservations;