import React, { useState, useEffect } from 'react';
import { Calendar, Badge, Modal, Button, message, Spin, Select, Row, Col } from 'antd';
import dayjs from 'dayjs';
import { fetchVenueCalendar, createReservation } from '../services/reservationService';
import './VenueCalendar.css';

const { Option } = Select;

const VenueCalendar = ({ venueId }) => {
  const [calendarData, setCalendarData] = useState({});
  const [selectedDate, setSelectedDate] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(dayjs().month());
  const [currentYear, setCurrentYear] = useState(dayjs().year());

  useEffect(() => {
    loadCalendarData();
  }, [venueId, currentMonth, currentYear]);

  const loadCalendarData = async () => {
    setIsLoading(true);
    try {
      const startDate = dayjs().year(currentYear).month(currentMonth).startOf('month').format('YYYY-MM-DD');
      const endDate = dayjs().year(currentYear).month(currentMonth).endOf('month').format('YYYY-MM-DD');
      const data = await fetchVenueCalendar(venueId, startDate, endDate);
      setCalendarData(data);
    } catch (error) {
      message.error('获取日历数据失败');
    } finally {
      setIsLoading(false);
    }
  };

  const dateCellRender = (value) => {
    const dateStr = value.format('YYYY-MM-DD');
    const dayData = calendarData[dateStr];

    if (!dayData || dayData.length === 0) {
      return <div className="cell-content closed">闭馆</div>;
    }

    const totalCapacity = dayData.reduce((sum, slot) => sum + slot.capacity, 0);
    
    if (totalCapacity <= 0) {
      return <div className="cell-content full">已约满</div>;
    }

    return <div className="cell-content available">剩余: {totalCapacity}</div>;
  };

  const disabledDate = (current) => {
    const dateStr = current.format('YYYY-MM-DD');
    const dayData = calendarData[dateStr];
    return !dayData || dayData.length === 0;
  };

  const handleDateSelect = (value) => {
    const dateStr = value.format('YYYY-MM-DD');
    const dayData = calendarData[dateStr];
    if (dayData && dayData.length > 0) {
      setSelectedDate(value);
      setIsModalVisible(true);
    }
  };

  const handleReservation = async (timeSlot) => {
    try {
      await createReservation(venueId, {
        date: selectedDate.format('YYYY-MM-DD'),
        start_time: timeSlot.start_time,
        end_time: timeSlot.end_time,
      });
      message.success('预约成功');
      setIsModalVisible(false);
      loadCalendarData();
    } catch (error) {
      message.error('预约失败');
    }
  };

  const headerRender = ({ value, type, onChange, onTypeChange }) => {
    return (
      <div style={{ padding: 8 }}>
        <Row gutter={8} justify="end">
          <Col>
            <Select
              value={value.month()}
              onChange={(newMonth) => {
                const now = value.clone().month(newMonth);
                onChange(now);
                setCurrentMonth(newMonth);
              }}
            >
              {Array.from({ length: 12 }, (_, i) => (
                <Option key={i} value={i}>
                  {dayjs().month(i).format('MMMM')}
                </Option>
              ))}
            </Select>
          </Col>
          <Col>
            <Select
              value={value.year()}
              onChange={(newYear) => {
                const now = value.clone().year(newYear);
                onChange(now);
                setCurrentYear(newYear);
              }}
            >
              {[currentYear - 1, currentYear, currentYear + 1].map((year) => (
                <Option key={year} value={year}>
                  {year}
                </Option>
              ))}
            </Select>
          </Col>
        </Row>
      </div>
    );
  };

  return (
    <div className="venue-calendar">
      <Spin spinning={isLoading}>
        <Calendar 
          dateCellRender={dateCellRender} 
          onSelect={handleDateSelect}
          headerRender={headerRender}
          validRange={[dayjs(), dayjs().add(2, 'month')]}
          disabledDate={disabledDate}
        />
      </Spin>
      <Modal
        title={`选择入馆时段 - ${selectedDate ? selectedDate.format('YYYY-MM-DD') : ''}`}
        visible={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
        <div className="time-slots">
          {selectedDate && calendarData[selectedDate.format('YYYY-MM-DD')]?.map((slot) => (
            <Button
              key={slot.id}
              onClick={() => handleReservation(slot)}
              type="primary"
              disabled={slot.capacity <= 0}
              className="time-slot-button"
            >
              {dayjs(slot.start_time, 'HH:mm:ss').format('HH:mm')} - {dayjs(slot.end_time, 'HH:mm:ss').format('HH:mm')} 
              (剩余: {slot.capacity})
            </Button>
          ))}
        </div>
      </Modal>
    </div>
  );
};

export default VenueCalendar;