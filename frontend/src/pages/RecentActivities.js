import React, { useState, useEffect } from 'react';
import { Row, Col, Select, Button, Spin, message } from 'antd';
import ActivityTimeline from '../components/ActivityTimeline';
import { fetchRecentActivities } from '../services/activityService';

const RecentActivities = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [limit, setLimit] = useState(5);

  useEffect(() => {
    loadActivities();
  }, []);

  const loadActivities = async () => {
    setLoading(true);
    try {
      const data = await fetchRecentActivities(limit);
      setActivities(data);
    } catch (error) {
      message.error('Failed to load activities');
    } finally {
      setLoading(false);
    }
  };

  const handleLimitChange = (value) => {
    setLimit(value);
  };

  const handleLoadMore = () => {
    loadActivities();
  };

  return (
    <Spin spinning={loading}>
      <h1>Recent Activities</h1>
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Select
            style={{ width: '100%' }}
            placeholder="Number of activities to show"
            onChange={handleLimitChange}
            value={limit}
          >
            <Select.Option value={5}>5</Select.Option>
            <Select.Option value={10}>10</Select.Option>
            <Select.Option value={20}>20</Select.Option>
          </Select>
        </Col>
        <Col span={12}>
          <Button type="primary" onClick={handleLoadMore} style={{ width: '100%' }}>
            Load Activities
          </Button>
        </Col>
      </Row>
      <Row style={{ marginTop: 20 }}>
        <Col span={24}>
          <ActivityTimeline activities={activities} />
        </Col>
      </Row>
    </Spin>
  );
};

export default RecentActivities;