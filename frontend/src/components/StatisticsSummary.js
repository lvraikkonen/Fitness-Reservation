import React, { useState, useEffect } from 'react';
import { Card, Statistic, Row, Col, Spin } from 'antd';
import { getStatisticsSummary } from '../services/statisticsService';

const StatisticsSummary = () => {
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        const data = await getStatisticsSummary();
        setStatistics(data);
      } catch (error) {
        console.error('Failed to fetch statistics summary:', error);
        setError('Failed to load statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStatistics();
  }, []);

  if (loading) {
    return <Card><Spin /></Card>;
  }

  if (error) {
    return <Card>{error}</Card>;
  }

  return (
    <Card title="Reservation Statistics">
      <Row gutter={16}>
        <Col span={32}>
          <Statistic 
            title="Total Reservations" 
            value={statistics?.total_reservations ?? 'N/A'} 
          />
        </Col>
        <Col span={32}>
          <Statistic 
            title="Most Active User" 
            value={statistics?.most_active_user ?? 'N/A'} 
          />
        </Col>
        <Col span={32}>
          <Statistic 
            title="Average Reservations per User" 
            value={statistics?.average_reservations ?? 'N/A'} 
            precision={2}
          />
        </Col>
      </Row>
    </Card>
  );
};

export default StatisticsSummary;