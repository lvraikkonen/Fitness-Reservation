import React, { useState, useEffect } from 'react';
import { Form, Input, Select, Button, Card, message } from 'antd';

const { Option } = Select;

const UserProfilePage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // 这里通常会从API获取用户信息
    // 现在我们用模拟数据
    form.setFieldsValue({
      name: '张三',
      department: '技术部',
      phone: '13800138000',
      email: 'zhangsan@example.com',
      preferredSport: 'yoga',
    });
  }, [form]);

  const onFinish = (values) => {
    setLoading(true);
    // 这里应该调用API来更新用户信息
    console.log('Updated profile:', values);
    setTimeout(() => {
      setLoading(false);
      message.success('个人信息更新成功');
    }, 1000);
  };

  return (
    <Card title="个人资料" style={{ maxWidth: 600, margin: '20px auto' }}>
      <Form form={form} layout="vertical" onFinish={onFinish}>
        <Form.Item name="name" label="姓名" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="department" label="部门" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="phone" label="联系电话" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="email" label="邮箱" rules={[{ required: true, type: 'email' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="preferredSport" label="喜好的运动类型">
          <Select>
            <Option value="yoga">瑜伽</Option>
            <Option value="weightlifting">举重</Option>
            <Option value="cardio">有氧运动</Option>
            <Option value="swimming">游泳</Option>
          </Select>
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            保存修改
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default UserProfilePage;