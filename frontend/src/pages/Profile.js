import React, { useState, useEffect } from 'react';
import { Card, Avatar, Typography, Form, Input, Button, message, Skeleton, Upload, Select, TimePicker } from 'antd';
import { UserOutlined, MailOutlined, PhoneOutlined, BankOutlined, HeartOutlined, ClockCircleOutlined, UploadOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { getCurrentUserProfile, updateUserProfile, uploadUserAvatar } from '../services/userService';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { Option } = Select;

const sportOptions = [
  'Basketball', 'Football', 'Tennis', 'Swimming', 'Badminton', 'Yoga'
];

const timeOptions = [
  '06:00-08:00', '08:00-10:00', '10:00-12:00', '12:00-14:00',
  '14:00-16:00', '16:00-18:00', '18:00-20:00', '20:00-22:00'
];

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
      form.setFieldsValue({
        ...userData,
        preferred_sports: userData.preferred_sports ? userData.preferred_sports.split(',') : [],
        preferred_time: userData.preferred_time ? userData.preferred_time.split(',') : []
      });
      setAvatarUrl(userData.avatar_url);
      updateUser(userData);
      setLoading(false);
    } catch (error) {
      message.error('Failed to fetch user profile: ' + error.message);
      setLoading(false);
    }
  };

  const onFinish = async (values) => {
    try {
      setLoading(true);
      const updatedValues = {
        ...values,
        preferred_sports: values.preferred_sports.join(','),
        preferred_time: values.preferred_time.join(',')
      };
      const updatedUser = await updateUserProfile(updatedValues);
      updateUser(updatedUser);
      message.success('Profile updated successfully');
    } catch (error) {
      message.error('Failed to update profile: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarUpload = async (info) => {
    const { status, originFileObj } = info.file;
    
    if (status !== 'uploading') {
      try {
        const response = await uploadUserAvatar(originFileObj);
        setAvatarUrl(response.avatar_url);
        updateUser({ ...user, avatar_url: response.avatar_url });
        message.success('Avatar uploaded successfully');
      } catch (error) {
        message.error('Avatar upload failed: ' + error.message);
      }
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
          <Select
            mode="multiple"
            style={{ width: '100%' }}
            placeholder="Select your preferred sports"
            optionLabelProp="label"
          >
            {sportOptions.map(sport => (
              <Option value={sport} label={sport} key={sport}>
                <div className="demo-option-label-item">
                  <span role="img" aria-label={sport}>
                    {
                     sport === 'Basketball' ? '🏀' : 
                     sport === 'Football' ? '⚽' : 
                     sport === 'Tennis' ? '🎾' :
                     sport === 'Yoga' ? '🧘' :
                     sport === 'Badminton' ? '🏸' :
                     sport === 'Swimming' ? '🏊' : ''}
                  </span>
                  {sport}
                </div>
              </Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item name="preferred_time" label="Preferred Time">
          <Select
            mode="multiple"
            style={{ width: '100%' }}
            placeholder="Select your preferred time slots"
            optionLabelProp="label"
          >
            {timeOptions.map(time => (
              <Option value={time} label={time} key={time}>
                <ClockCircleOutlined /> {time}
              </Option>
            ))}
          </Select>
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