import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Rate, message, List, Card, Typography, Select, Modal } from 'antd';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../components/MainLayout';
import { submitFeedback, getFeedbackList } from '../services/feedbackService';
import { getVenues } from '../services/venueService';

const { TextArea } = Input;
const { Title } = Typography;
const { Option } = Select;

const Feedback = () => {
  const [form] = Form.useForm();
  const [feedbackList, setFeedbackList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [venues, setVenues] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchFeedbackList();
    fetchVenues();
  }, []);

  const fetchFeedbackList = async () => {
    try {
      const data = await getFeedbackList();
      setFeedbackList(data);
    } catch (error) {
      message.error('Failed to fetch feedback list');
    }
  };

  const fetchVenues = async () => {
    try {
      const data = await getVenues();
      setVenues(data);
    } catch (error) {
      message.error('Failed to fetch venues');
    }
  };

  const onFinish = async (values) => {
    setLoading(true);
    try {
      await submitFeedback(values);
      message.success('Feedback submitted successfully');
      form.resetFields();
      fetchFeedbackList();
      setIsModalVisible(true);
    } catch (error) {
      message.error('Failed to submit feedback: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleModalOk = () => {
    setIsModalVisible(false);
    navigate('/dashboard');
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
  };

  return (
    <MainLayout>
      <div style={{ padding: '24px' }}>
        <Title level={2}>Feedback</Title>
        <Card title="Submit Feedback">
          <Form form={form} onFinish={onFinish} layout="vertical">
            <Form.Item name="venue_id" label="Venue" rules={[{ required: true, message: 'Please select a venue!' }]}>
              <Select>
                {venues.map(venue => (
                  <Option key={venue.id} value={venue.id}>{venue.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="title" label="Title" rules={[{ required: true, message: 'Please input a title!' }]}>
              <Input />
            </Form.Item>
            <Form.Item name="content" label="Content" rules={[{ required: true, message: 'Please input your feedback!' }]}>
              <TextArea rows={4} />
            </Form.Item>
            <Form.Item name="rating" label="Rating" rules={[{ required: true, message: 'Please give a rating!' }]}>
              <Rate />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading}>
                Submit Feedback
              </Button>
            </Form.Item>
          </Form>
        </Card>
        <Card title="Recent Feedback" style={{ marginTop: '24px' }}>
          <List
            itemLayout="horizontal"
            dataSource={feedbackList}
            renderItem={item => (
              <List.Item>
                <List.Item.Meta
                  title={item.title}
                  description={
                    <>
                      <Rate disabled defaultValue={item.rating} />
                      <p>{item.content}</p>
                    </>
                  }
                />
              </List.Item>
            )}
          />
        </Card>
        <Modal
          title="Feedback Submitted"
          visible={isModalVisible}
          onOk={handleModalOk}
          onCancel={handleModalCancel}
          footer={[
            <Button key="back" onClick={handleModalCancel}>
              Stay on this page
            </Button>,
            <Button key="submit" type="primary" onClick={handleModalOk}>
              Return to Dashboard
            </Button>,
          ]}
        >
          <p>Your feedback has been submitted successfully. What would you like to do next?</p>
        </Modal>
      </div>
    </MainLayout>
  );
};

export default Feedback;