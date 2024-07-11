import React, { useEffect } from 'react';
import { Card, Avatar, Typography, Form, Input, Button, message } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import MainLayout from '../components/MainLayout';
import { useAuth } from '../contexts/AuthContext';
import { updateUserProfile } from '../services/auth';

const { Title } = Typography;

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [form] = Form.useForm();

  useEffect(() => {
    if (user) {
      form.setFieldsValue(user);
    }
  }, [user, form]);

  const onFinish = async (values) => {
    try {
      const updatedUser = await updateUserProfile(values);
      updateUser(updatedUser);
      message.success('Profile updated successfully');
    } catch (error) {
      message.error('Failed to update profile: ' + error.message);
    }
  };

  if (!user) return <div>Loading...</div>;

  return (
    <MainLayout>
      <Card>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Avatar size={64} icon={<UserOutlined />} />
          <Title level={2}>{user.username}</Title>
        </div>
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item name="full_name" label="Full Name">
            <Input />
          </Form.Item>
          <Form.Item name="email" label="Email">
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="Phone">
            <Input />
          </Form.Item>
          <Form.Item name="department" label="Department">
            <Input />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              Update Profile
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </MainLayout>
  );
};

export default Profile;