import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const PrivateRoute = ({ children }) => {
  const location = useLocation();
  const { isAuthenticated, loading } = useAuth();

  console.log('PrivateRoute: ', { isAuthenticated, loading, location });

  if (loading) {
    console.log('PrivateRoute: Still loading');
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    console.log('PrivateRoute: Not authenticated, redirecting to login');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  console.log('PrivateRoute: Authenticated, rendering children');
  return children;
};

export default PrivateRoute;