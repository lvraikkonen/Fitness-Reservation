import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../services/auth';

const PrivateRoute = ({ children }) => {
  if (!isAuthenticated()) {
    // 如果用户未登录，重定向到登录页面
    return <Navigate to="/" replace />;
  }

  return children;
};

export default PrivateRoute;