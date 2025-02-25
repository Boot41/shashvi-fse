import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();
  
  console.log('PublicRoute: loading:', loading);
  console.log('PublicRoute: isAuthenticated:', isAuthenticated());
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (isAuthenticated()) {
    // Redirect to the page they were trying to visit
    return <Navigate to={location.state?.from?.pathname || '/dashboard'} replace />;
  }

  // Render the children if not authenticated
  return children;
};

export default PublicRoute;
