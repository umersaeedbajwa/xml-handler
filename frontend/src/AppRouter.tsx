import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout, ProtectedRoute } from './components';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import DomainsPage from './pages/DomainsPage';
import ExtensionsPage from './pages/ExtensionsPage';
import VoicemailsPage from './pages/VoicemailsPage';

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
                  
                  {/* FreeSWITCH Management routes */}
                  <Route path="/domains" element={<DomainsPage />} />
                  <Route path="/extensions" element={<ExtensionsPage />} />
                  <Route path="/voicemails" element={<VoicemailsPage />} />
                  
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
