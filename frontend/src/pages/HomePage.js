import React from 'react';
import { Card, Row, Col, Button } from 'antd';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>欢迎使用健身场馆预约系统</h1>
      <Row gutter={16}>
        <Col span={8}>
          <Card title="预约健身房" extra={<Link to="/booking"><Button type="primary">去预约</Button></Link>}>
            快速预约您喜欢的健身房，开始您的健身之旅。
          </Card>
        </Col>
        <Col span={8}>
          <Card title="查看健身房" extra={<Link to="/gyms"><Button type="primary">查看列表</Button></Link>}>
            浏览所有可用的健身房，了解设施和位置信息。
          </Card>
        </Col>
        <Col span={8}>
          <Card title="个人资料" extra={<Link to="/profile"><Button type="primary">查看资料</Button></Link>}>
            管理您的个人信息和健身偏好设置。
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default HomePage;