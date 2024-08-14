import React, { useState, useEffect } from 'react';
import { Card, Avatar, Typography, Form, Input, Button, message, Skeleton, Upload } from 'antd';
import { UserOutlined, MailOutlined, PhoneOutlined, BankOutlined, HeartOutlined, ClockCircleOutlined, UploadOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { getCurrentUserProfile, updateUserProfile, uploadUserAvatar } from '../services/userService';

const { Title, Text } = Typography;

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(true);
  const [avatarUrl, setAvatarUrl] = useState('');

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const userData = await getCurrentUserProfile();
      form.setFieldsValue(userData);
      setAvatarUrl(userData.avatar_url);
      updateUser(userData);
      setLoading(false);
    } catch (error) {
      message.error('Failed to fetch user profile');
      setLoading(false);
    }
  };

  const onFinish = async (values) => {
    try {
      setLoading(true);
      const updatedUser = await updateUserProfile(values);
      updateUser(updatedUser);
      message.success('Profile updated successfully');
    } catch (error) {
      message.error('Failed to update profile: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarUpload = async (info) => {
    const { status } = info.file;
    
    if (status === 'done') {
      try {
        // 模拟文件上传
        const reader = new FileReader();
        reader.onload = async (e) => {
          const base64Image = e.target.result;
          const response = await uploadUserAvatar(base64Image);
          setAvatarUrl(response.avatar_url);
          updateUser({ ...user, avatar_url: response.avatar_url });
          message.success('Avatar uploaded successfully');
        };
        reader.readAsDataURL(info.file.originFileObj);
      } catch (error) {
        message.error('Avatar upload failed');
      }
    } else if (status === 'error') {
      message.error(`${info.file.name} file upload failed.`);
    }
  };

  const beforeUpload = (file) => {
    const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
    if (!isJpgOrPng) {
      message.error('You can only upload JPG/PNG file!');
    }
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
      message.error('Image must smaller than 2MB!');
    }
    return isJpgOrPng && isLt2M;
  };

  if (loading) return <Skeleton active />;

  return (
    <Card>
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <Upload
          name="avatar"
          listType="picture-card"
          className="avatar-uploader"
          showUploadList={false}
          beforeUpload={beforeUpload}
          onChange={handleAvatarUpload}
          customRequest={({ file, onSuccess }) => {
            setTimeout(() => {
              onSuccess("ok");
            }, 0);
          }}
        >
          {avatarUrl ? (
            <Avatar size={100} src={avatarUrl} />
          ) : (
            <div>
              <UploadOutlined />
              <div style={{ marginTop: 8 }}>Upload</div>
            </div>
          )}
        </Upload>
        <Title level={2}>{user.username}</Title>
        <Text type="secondary">{user.role}</Text>
      </div>
      <Form form={form} layout="vertical" onFinish={onFinish}>
        <Form.Item name="full_name" label="Full Name" rules={[{ required: true }]}>
          <Input prefix={<UserOutlined />} />
        </Form.Item>
        <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
          <Input prefix={<MailOutlined />} />
        </Form.Item>
        <Form.Item name="phone" label="Phone" rules={[{ required: true }]}>
          <Input prefix={<PhoneOutlined />} />
        </Form.Item>
        <Form.Item name="department" label="Department">
          <Input prefix={<BankOutlined />} />
        </Form.Item>
        <Form.Item name="preferred_sports" label="Preferred Sports">
          <Input prefix={<HeartOutlined />} />
        </Form.Item>
        <Form.Item name="preferred_time" label="Preferred Time">
          <Input prefix={<ClockCircleOutlined />} />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            Update Profile
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default Profile;