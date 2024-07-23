import React, { useState, useEffect } from 'react';
import { Calendar, Modal, Button, message, Spin, Select, Row, Col } from 'antd';
import dayjs from 'dayjs';
import { fetchVenueCalendar, createReservation } from '../services/reservationService';
import './VenueCalendar.css';
import { useAuth } from '../contexts/AuthContext';

const { Option } = Select;

const VenueCalendar = ({ venueId }) => {
  const [calendarData, setCalendarData] = useState({});
  const [selectedDate, setSelectedDate] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(dayjs().month());
  const [currentYear, setCurrentYear] = useState(dayjs().year());
  const { user } = useAuth();  // 使用 AuthContext 获取用户信息

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
    return !dayData || dayData.length === 0 || current < dayjs().startOf('day');
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
        start_time: timeSlot.startTime,
        end_time: timeSlot.endTime,
        user_id: user.id,
        venue_id: venueId,
        status: 'pending', // 或者其他适当的初始状态
        is_recurring: false,
        // 如果需要，可以添加 recurring_pattern 和 recurrence_end_date
      });
      message.success('预约成功');
      setIsModalVisible(false);
      loadCalendarData();
    } catch (error) {
      console.error('Reservation error:', error);
      message.error('预约失败：' + (error.response?.data?.detail || error.message));
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
        title={`选择预约时段 - ${selectedDate ? selectedDate.format('YYYY-MM-DD') : ''}`}
        visible={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
        <div className="time-slots">
          {selectedDate && calendarData[selectedDate.format('YYYY-MM-DD')] ? (
            calendarData[selectedDate.format('YYYY-MM-DD')].map((slot) => (
              <Button
                key={slot.id}
                onClick={() => handleReservation(slot)}
                type="primary"
                disabled={slot.capacity <= 0}
                className="time-slot-button"
              >
                {slot.startTime.substring(0, 5)} - {slot.endTime.substring(0, 5)}
                (剩余: {slot.capacity})
              </Button>
            ))
          ) : (
            <p>该日期没有可用的预约时段。</p>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default VenueCalendar;