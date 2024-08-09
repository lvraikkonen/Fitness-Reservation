import React, { useState, useEffect } from 'react';
import { Calendar, Modal, Button, message, Spin, Select, Row, Col, List } from 'antd';
import dayjs from 'dayjs';
import { fetchVenueCalendar, createReservation, cancelReservation, fetchUserReservations } from '../services/reservationService';
import './VenueCalendar.css';
import { useAuth } from '../contexts/AuthContext';

const { Option } = Select;

const VenueCalendar = ({ venueId }) => {
  const [calendarData, setCalendarData] = useState({});
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [userReservations, setUserReservations] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(dayjs().month());
  const [currentYear, setCurrentYear] = useState(dayjs().year());
  const { user } = useAuth();

  useEffect(() => {
    loadCalendarData();
    loadUserReservations();
  }, [venueId, currentMonth, currentYear]);

  const loadCalendarData = async () => {
    setIsLoading(true);
    try {
      const startDate = dayjs().format('YYYY-MM-DD');
      const endDate = dayjs().add(6, 'day').format('YYYY-MM-DD');
      const data = await fetchVenueCalendar(venueId, startDate, endDate);
      console.log('Fetched calendar data:', data);  // 添加日志
  
      setCalendarData(data);
  
      console.log('Formatted calendar data:', data);  // 添加日志
    } catch (error) {
      console.error('获取日历数据失败:', error);
      message.error('获取日历数据失败');
    } finally {
      setIsLoading(false);
    }
  };

  const loadUserReservations = async () => {
    try {
      const reservations = await fetchUserReservations(user.id, venueId);
      console.log('Fetched user reservations:', reservations);  // 添加日志
      setUserReservations(Array.isArray(reservations) ? reservations : []);
    } catch (error) {
      console.error('Error fetching user reservations:', error);
      message.error('获取用户预约失败');
    }
  };

  const dateCellRender = (value) => {
    const dateStr = value.format('YYYY-MM-DD');
    const dayData = calendarData[dateStr] || [];
  
    if (dayData.length === 0) {
      return <div className="cell-content closed">闭馆</div>;
    }
  
    const totalAvailableCapacity = dayData.reduce((sum, slot) => sum + slot.availableCapacity, 0);
    const totalCapacity = dayData.reduce((sum, slot) => sum + slot.totalCapacity, 0);
    
    if (totalAvailableCapacity <= 0) {
      return <div className="cell-content full">已约满</div>;
    }
  
    return (
      <div className="cell-content available">
        剩余: {totalAvailableCapacity}/{totalCapacity}
      </div>
    );
  };
  
  const disabledDate = (current) => {
    const dateStr = current.format('YYYY-MM-DD');
    const dayData = calendarData[dateStr] || [];
    const totalAvailableCapacity = dayData.reduce((sum, slot) => sum + slot.availableCapacity, 0);
    return dayData.length === 0 || totalAvailableCapacity <= 0 || current < dayjs().startOf('day');
  };

  const handleDateSelect = (value) => {
    const dateStr = value.format('YYYY-MM-DD');
    const dayData = calendarData[dateStr] || [];
    if (dayData.length > 0) {
      setSelectedDate(value);
      setIsModalVisible(true);
    }
  };

  const handleSlotSelection = (slot) => {
    setSelectedSlot(slot);
  };

  const handleReservationConfirmation = async () => {
    if (!selectedSlot) {
      message.warning('请先选择一个时间段');
      return;
    }

    try {
      await createReservation(venueId, {
        date: selectedDate.format('YYYY-MM-DD'),
        start_time: selectedSlot.startTime,
        end_time: selectedSlot.endTime,
        user_id: user.id,
        venue_id: venueId,
        status: 'pending',
        is_recurring: false,
      });
      message.success('预约成功');
      setIsModalVisible(false);
      
      // 更新本地状态
      const dateKey = selectedDate.format('YYYY-MM-DD');
      setCalendarData(prevData => {
        const updatedSlots = (prevData[dateKey] || []).map(slot => 
          slot.id === selectedSlot.id ? { ...slot, capacity: (slot.capacity || 0) - 1 } : slot
        );
        return { ...prevData, [dateKey]: updatedSlots };
      });

      setSelectedSlot(null);
      await loadUserReservations();
    } catch (error) {
      console.error('Reservation error:', error);
      message.error('预约失败：' + (error.response?.data?.detail || error.message));
    }
  };

  const handleReservationCancellation = async (reservationId) => {
    try {
      await cancelReservation(reservationId);
      message.success('预约已成功取消');

      const cancelledReservation = userReservations.find(r => r.id === reservationId);
      if (cancelledReservation) {
        const dateKey = dayjs(cancelledReservation.date).format('YYYY-MM-DD');
        setCalendarData(prevData => {
          const updatedSlots = (prevData[dateKey] || []).map(slot => 
            (slot.startTime === cancelledReservation.start_time && slot.endTime === cancelledReservation.end_time)
              ? { ...slot, capacity: (slot.capacity || 0) + 1 }
              : slot
          );
          return { ...prevData, [dateKey]: updatedSlots };
        });
      }

      await loadUserReservations();
    } catch (error) {
      console.error('Cancellation error:', error);
      message.error('取消预约失败：' + (error.response?.data?.detail || error.message));
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
        onCancel={() => {
          setIsModalVisible(false);
          setSelectedSlot(null);
        }}
        footer={[
          <Button key="cancel" onClick={() => setIsModalVisible(false)}>
            取消
          </Button>,
          <Button 
            key="submit" 
            type="primary" 
            onClick={handleReservationConfirmation}
            disabled={!selectedSlot}
          >
            确认预约
          </Button>
        ]}
      >
        <div className="time-slots">
          {selectedDate && calendarData[selectedDate.format('YYYY-MM-DD')] ? (
            calendarData[selectedDate.format('YYYY-MM-DD')].map((slot) => (
              <Button
                key={slot.id}
                onClick={() => handleSlotSelection(slot)}
                type={selectedSlot && selectedSlot.id === slot.id ? "primary" : "default"}
                disabled={slot.availableCapacity <= 0}
                className="time-slot-button"
              >
                {slot.startTime.substring(0, 5)} - {slot.endTime.substring(0, 5)}
                (剩余: {slot.availableCapacity}/{slot.totalCapacity})
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