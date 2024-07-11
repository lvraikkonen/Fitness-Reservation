import React, { useState } from 'react';
import { Form, Input, Button, message, Modal } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { requestPasswordReset, resetPassword } from '../services/auth';

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [isResetModalVisible, setIsResetModalVisible] = useState(false);
  const [isNewPasswordModalVisible, setIsNewPasswordModalVisible] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetToken, setResetToken] = useState('');

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const user = await login(values);
      message.success('Login successful');
      
      // 根据用户角色决定跳转路径
      const from = location.state?.from?.pathname || 
                   (user.role === 1 ? '/admin' : '/dashboard');
      
      navigate(from, { replace: true });
    } catch (error) {
      console.error('Login error:', error);
      message.error('Login failed: ' + (error.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };
  
  const showResetModal = () => {
    setIsResetModalVisible(true);
  };

  const handleResetRequest = async () => {
    try {
      await requestPasswordReset(resetEmail);
      message.success('Password reset link sent to your email');
      setIsResetModalVisible(false);
      setIsNewPasswordModalVisible(true);
    } catch (error) {
      message.error('Failed to send reset link: ' + error.message);
    }
  };

  const handleResetPassword = async (values) => {
    try {
      await resetPassword(resetToken, values.newPassword);
      message.success('Password reset successful. You can now login with your new password.');
      setIsNewPasswordModalVisible(false);
    } catch (error) {
      message.error('Failed to reset password: ' + error.message);
    }
  };

  return (
    <div style={{ maxWidth: 300, margin: '0 auto', marginTop: 100 }}>
      <h2>Login</h2>
      <Form form={form} onFinish={onFinish}>
        <Form.Item
          name="username"
          rules={[{ required: true, message: 'Please input your Username!' }]}
        >
          <Input prefix={<UserOutlined />} placeholder="Username" />
        </Form.Item>
        <Form.Item
          name="password"
          rules={[{ required: true, message: 'Please input your Password!' }]}
        >
          <Input.Password prefix={<LockOutlined />} placeholder="Password" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} style={{ width: '100%' }}>
            Log in
          </Button>
        </Form.Item>
      </Form>
      <div>
        <a onClick={showResetModal}>Forgot password?</a>
      </div>
      <div>
        Don't have an account? <Link to="/register">Register here</Link>
      </div>

      <Modal
        title="Reset Password"
        visible={isResetModalVisible}
        onOk={handleResetRequest}
        onCancel={() => setIsResetModalVisible(false)}
      >
        <Input
          prefix={<MailOutlined />}
          placeholder="Enter your email"
          value={resetEmail}
          onChange={(e) => setResetEmail(e.target.value)}
        />
      </Modal>

      <Modal
        title="Enter New Password"
        visible={isNewPasswordModalVisible}
        onCancel={() => setIsNewPasswordModalVisible(false)}
        footer={null}
      >
        <Form onFinish={handleResetPassword}>
          <Form.Item
            name="resetToken"
            rules={[{ required: true, message: 'Please input the reset token from your email!' }]}
          >
            <Input placeholder="Reset Token" onChange={(e) => setResetToken(e.target.value)} />
          </Form.Item>
          <Form.Item
            name="newPassword"
            rules={[
              { required: true, message: 'Please input your new password!' },
              { min: 8, message: 'Password must be at least 8 characters long!' },
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="New Password" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" style={{ width: '100%' }}>
              Reset Password
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Login;