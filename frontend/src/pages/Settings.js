import React, { useState, useEffect } from 'react';
import { Card, Switch, Typography, Form, Button, message, Skeleton } from 'antd';
import { MailOutlined, MessageOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { getUserSettings, updateUserSettings } from '../services/userService';

const { Title } = Typography;

const UserSettings = () => {
  const { user, updateUser } = useAuth();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserSettings();
  }, []);

  const fetchUserSettings = async () => {
    try {
      const settings = await getUserSettings();
      form.setFieldsValue(settings);
      setLoading(false);
    } catch (error) {
      message.error('Failed to fetch user settings');
      setLoading(false);
    }
  };

  const onFinish = async (values) => {
    try {
      setLoading(true);
      const updatedSettings = await updateUserSettings(values);
      updateUser({ ...user, settings: updatedSettings });
      message.success('Settings updated successfully');
    } catch (error) {
      message.error('Failed to update settings: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Skeleton active />;

  return (
    <Card>
      <Title level={2}>User Settings</Title>
      <Form form={form} layout="vertical" onFinish={onFinish}>
        <Form.Item name="email_notifications" label="Email Notifications" valuePropName="checked">
          <Switch checkedChildren={<MailOutlined />} unCheckedChildren={<MailOutlined />} />
        </Form.Item>
        <Form.Item name="sms_notifications" label="SMS Notifications" valuePropName="checked">
          <Switch checkedChildren={<MessageOutlined />} unCheckedChildren={<MessageOutlined />} />
        </Form.Item>
        {/* 可以在这里添加其他设置选项 */}
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            Save Settings
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default UserSettings;