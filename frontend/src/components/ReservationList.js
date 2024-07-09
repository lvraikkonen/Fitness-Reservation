import React from 'react';
import { List, Button } from 'antd';
import dayjs from 'dayjs';

const ReservationList = ({ reservations, onCancel }) => {
  return (
    <List
      header={<div>My Reservations</div>}
      bordered
      dataSource={reservations}
      renderItem={item => (
        <List.Item
          actions={[
            <Button onClick={() => onCancel(item.id)} type="link" danger>
              Cancel
            </Button>
          ]}
        >
          <List.Item.Meta
            title={`Reservation for ${dayjs(item.date).format('YYYY-MM-DD')}`}
            description={
              <>
                <p>Time: {item.start_time} - {item.end_time}</p>
                <p>Venue: {item.sport_venue_name} - {item.venue_name}</p>
                <p>Status: {item.status}</p>
              </>
            }
          />
        </List.Item>
      )}
    />
  );
};

export default ReservationList;