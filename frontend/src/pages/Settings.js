import React, { useEffect } from 'react';
import { Card, Switch, Typography, Form, Button, message } from 'antd';
import MainLayout from '../components/MainLayout';
import { useAuth } from '../contexts/AuthContext';
import { updateUserSettings } from '../services/auth';

const { Title } = Typography;

const Settings = () => {
  const { user, updateUser } = useAuth();
  const [form] = Form.useForm();

  useEffect(() => {
    if (user && user.settings) {
      form.setFieldsValue(user.settings);
    }
  }, [user, form]);

  const onFinish = async (values) => {
    try {
      const updatedUser = await updateUserSettings(values);
      updateUser(updatedUser);
      message.success('Settings updated successfully');
    } catch (error) {
      message.error('Failed to update settings: ' + error.message);
    }
  };

  if (!user) return <div>Loading...</div>;

  return (
    <MainLayout>
      <Card>
        <Title level={2}>User Settings</Title>
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item name="email_notifications" label="Email Notifications" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="sms_notifications" label="SMS Notifications" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="dark_mode" label="Dark Mode" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              Save Settings
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </MainLayout>
  );
};

export default Settings;