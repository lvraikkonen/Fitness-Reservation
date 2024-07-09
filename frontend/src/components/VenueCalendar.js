import React, { useState, useEffect, forwardRef, useImperativeHandle, useRef } from 'react';
import { Calendar, Badge, Pagination } from 'antd';
import dayjs from 'dayjs';
import { fetchVenueCalendar } from '../services/reservationService';

const VenueCalendar = forwardRef(({ venueId }, ref) => {
  const [calendarData, setCalendarData] = useState({});
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 });
  const containerRef = useRef(null);

  useEffect(() => {
    if (venueId) {
      loadCalendarData();
    }
  }, [venueId, currentPage]);

  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        setContainerSize({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight,
        });
      }
    };

    window.addEventListener('resize', updateSize);
    updateSize();

    return () => window.removeEventListener('resize', updateSize);
  }, []);

  useImperativeHandle(ref, () => ({
    refreshCalendar: loadCalendarData
  }));

  const loadCalendarData = async () => {
    try {
      const data = await fetchVenueCalendar(venueId, null, null, currentPage);
      setCalendarData(data.calendar_data || {});
      setTotalPages(data.total_pages || 1);
    } catch (error) {
      console.error('Failed to load calendar data', error);
      setCalendarData({});
      setTotalPages(1);
    }
  };

  const dateCellRender = (value) => {
    const dateStr = value.format('YYYY-MM-DD');
    const listData = calendarData[dateStr] || [];
    
    return (
      <ul className="events">
        {listData.map(item => (
          <li key={item.id}>
            <Badge 
              status={item.reservations && item.reservations.length > 0 ? 'success' : 'default'} 
              text={`${item.start_time}-${item.end_time} (${item.reservations ? item.reservations.length : 0})`} 
            />
          </li>
        ))}
      </ul>
    );
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ flex: 1, overflow: 'auto' }}>
        <Calendar 
          dateCellRender={dateCellRender} 
          style={{ width: '100%', height: '100%' }}
        />
      </div>
      <Pagination 
        current={currentPage} 
        total={totalPages * 10} 
        onChange={handlePageChange} 
        style={{ marginTop: '10px', textAlign: 'center' }}
      />
    </div>
  );
});

export default VenueCalendar;