import React from 'react';
import { Form, DatePicker, TimePicker, Button } from 'antd';
import dayjs from 'dayjs';

const ReservationForm = ({ onSubmit }) => {
  const [form] = Form.useForm();

  const handleSubmit = (values) => {
    onSubmit({
      date: dayjs(values.date).format('YYYY-MM-DD'),
      start_time: dayjs(values.time[0]).format('HH:mm'),
      end_time: dayjs(values.time[1]).format('HH:mm'),
    });
    form.resetFields();
  };

  return (
    <Form form={form} onFinish={handleSubmit} layout="inline">
      <Form.Item name="date" rules={[{ required: true, message: 'Please select a date' }]}>
        <DatePicker />
      </Form.Item>
      <Form.Item name="time" rules={[{ required: true, message: 'Please select a time range' }]}>
        <TimePicker.RangePicker format="HH:mm" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit">
          Create Reservation
        </Button>
      </Form.Item>
    </Form>
  );
};

export default ReservationForm;