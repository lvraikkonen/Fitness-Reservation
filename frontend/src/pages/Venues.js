import React, { useState, useEffect } from 'react';
import { Row, Col, Card, List, Input, Select, Spin, Modal, Button, message } from 'antd';
import { SearchOutlined, CalendarOutlined } from '@ant-design/icons';
import { getVenues, searchVenues, getVenueDetails } from '../services/venueService';
import VenueCalendar from '../components/VenueCalendar';

const { Search } = Input;
const { Option } = Select;

const Venues = () => {
  const [venues, setVenues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sportType, setSportType] = useState('all');
  const [selectedVenue, setSelectedVenue] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  const fetchVenues = async (search = '', type = 'all') => {
    setLoading(true);
    try {
      let data;
      if (type === 'all' && search.trim() === '') {
        data = await getVenues();
      } else {
        data = await searchVenues(search, type);
      }
      console.log('Fetched venues:', data);
      setVenues(data);
    } catch (error) {
      console.error('Error fetching venues:', error);
      message.error('Failed to fetch venues: ' + (error.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    console.log('Sport type changed to:', sportType);
    fetchVenues(searchTerm, sportType);
  }, [sportType]);

  const handleSearch = async (value) => {
    console.log('Search term:', value);
    setSearchTerm(value);
    fetchVenues(value, sportType);
  };

  const handleSportTypeChange = (value) => {
    console.log('Sport type selected:', value);
    setSportType(value);
  };

  const showVenueDetails = async (venueId) => {
    try {
      const details = await getVenueDetails(venueId);
      setSelectedVenue(details);
      setModalVisible(true);
    } catch (error) {
      message.error('Failed to fetch venue details');
    }
  };

  const renderVenueCard = (venue) => (
    <Card
      hoverable
      cover={<img alt={venue.name} src={venue.image_url} style={{ height: 200, objectFit: 'cover' }} />}
      onClick={() => showVenueDetails(venue.id)}
    >
      <Card.Meta
        title={venue.name}
        description={
          <>
            <p>{venue.location}</p>
            <p>Sport: {venue.sport_type}</p>
            <p>Capacity: {venue.capacity}</p>
          </>
        }
      />
    </Card>
  );

  return (
    <Spin spinning={loading}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Search
            placeholder="Search venues"
            onSearch={handleSearch}
            style={{ width: 200, marginRight: 16 }}
            prefix={<SearchOutlined />}
          />
          <Select
                style={{ width: 150 }}
                placeholder="Select sport type"
                onChange={handleSportTypeChange}
                value={sportType}
            >
                <Option value="all">All Sports</Option>
                <Option value="Basketball">Basketball</Option>
                <Option value="Tennis">Tennis</Option>
                <Option value="Swimming">Swimming</Option>
                <Option value="Soccer">Soccer</Option>
                <Option value="Yoga">Yoga</Option>
                <Option value="Badminton">Badminton</Option>
            </Select>
        </Col>
        <Col span={24}>
          <List
            grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 3, xl: 4, xxl: 4 }}
            dataSource={venues}
            renderItem={renderVenueCard}
          />
        </Col>
      </Row>

      <Modal
        title={selectedVenue?.name}
        visible={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setModalVisible(false)}>
            Close
          </Button>,
          <Button key="reserve" type="primary" icon={<CalendarOutlined />}>
            Make Reservation
          </Button>
        ]}
        width={800}
      >
        {selectedVenue && (
          <>
            <img src={selectedVenue.image_url} alt={selectedVenue.name} style={{ width: '100%', marginBottom: 16 }} />
            <p><strong>Location:</strong> {selectedVenue.sport_venue.location}</p>
            <p><strong>Sport Type:</strong> {selectedVenue.sport_type}</p>
            <p><strong>Capacity:</strong> {selectedVenue.capacity}</p>
            <p><strong>Description:</strong> {selectedVenue.description}</p>
            <p><strong>Notice:</strong> {selectedVenue.notice}</p>
            <VenueCalendar venueId={selectedVenue.id} />
          </>
        )}
      </Modal>
    </Spin>
  );
};

export default Venues;