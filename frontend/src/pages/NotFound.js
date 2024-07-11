import React from 'react';
import { Result, Button } from 'antd';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <Result
      status="404"
      title="404"
      subTitle="抱歉，您访问的页面不存在。"
      extra={
        <Link to="/dashboard">
          <Button type="primary">返回首页</Button>
        </Link>
      }
    />
  );
};

export default NotFound;