import React, { useState, useEffect } from 'react';
import { Form, Select, DatePicker, TimePicker, Button, Card, message } from 'antd';
import moment from 'moment';

const { Option } = Select;

const BookingPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [gyms, setGyms] = useState([]);

  useEffect(() => {
    // 这里应该从API获取健身房列表
    // 现在我们用模拟数据
    setGyms([
      { id: 1, name: '健身房A' },
      { id: 2, name: '健身房B' },
      { id: 3, name: '健身房C' },
    ]);
  }, []);

  const onFinish = (values) => {
    setLoading(true);
    // 这里应该调用API来创建预约
    console.log('Booking details:', {
      ...values,
      date: values.date.format('YYYY-MM-DD'),
      time: values.time.format('HH:mm'),
    });
    setTimeout(() => {
      setLoading(false);
      message.success('预约成功');
      form.resetFields();
    }, 1000);
  };

  return (
    <Card title="预约健身房" style={{ maxWidth: 600, margin: '20px auto' }}>
      <Form form={form} layout="vertical" onFinish={onFinish}>
        <Form.Item name="gym" label="选择健身房" rules={[{ required: true }]}>
          <Select placeholder="请选择健身房">
            {gyms.map(gym => (
              <Option key={gym.id} value={gym.id}>{gym.name}</Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item name="date" label="选择日期" rules={[{ required: true }]}>
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item name="time" label="选择时间" rules={[{ required: true }]}>
          <TimePicker format="HH:mm" style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            确认预约
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default BookingPage;