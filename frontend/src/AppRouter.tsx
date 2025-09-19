import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout, ProtectedRoute } from './components';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';

const AppRouter: React.FC = () => {
  return (
    <Router>
      <Routes>
        {/* Public route - Login */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected routes */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <AppLayout>
                <Routes>
                  {/* Default route redirects to dashboard */}
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  {/* Dashboard route */}
                  <Route path="/dashboard" element={<Dashboard />} />
                  
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </AppLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
};

export default AppRouter;
