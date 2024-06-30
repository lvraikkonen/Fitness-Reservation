import React, { useState, useEffect } from 'react';
import { List, Card, Button } from 'antd';
import { Link } from 'react-router-dom';

const GymListPage = () => {
  const [gyms, setGyms] = useState([]);

  useEffect(() => {
    // Here you would fetch the gym list from your API
    // For now, we'll use dummy data
    setGyms([
      { id: 1, name: '健身房A', location: '位置A', facilities: '设施A' },
      { id: 2, name: '健身房B', location: '位置B', facilities: '设施B' },
      { id: 3, name: '健身房C', location: '位置C', facilities: '设施C' },
    ]);
  }, []);

  return (
    <div style={{ padding: '20px' }}>
      <h1>健身场馆列表</h1>
      <List
        grid={{ gutter: 16, column: 3 }}
        dataSource={gyms}
        renderItem={(gym) => (
          <List.Item>
            <Card title={gym.name}>
              <p>位置: {gym.location}</p>
              <p>设施: {gym.facilities}</p>
              <Link to={`/booking?gymId=${gym.id}`}>
                <Button type="primary">预约</Button>
              </Link>
            </Card>
          </List.Item>
        )}
      />
    </div>
  );
};

export default GymListPage;