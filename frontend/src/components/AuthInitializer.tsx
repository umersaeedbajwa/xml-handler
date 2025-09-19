import React, { useEffect, useState } from 'react';
import { Spin } from 'antd';
import { useAuthStore } from '../store/authStore';

interface AuthInitializerProps {
  children: React.ReactNode;
}

const AuthInitializer: React.FC<AuthInitializerProps> = ({ children }) => {
  const [isInitialized, setIsInitialized] = useState(false);
  const { token, getCurrentUser, logout } = useAuthStore();

  useEffect(() => {
    const initializeAuth = async () => {
      if (token) {
        try {
          await getCurrentUser();
        } catch (error) {
          // Token might be invalid, clear it
          console.error('Token validation failed:', error);
          await logout();
        }
      }
      setIsInitialized(true);
    };

    initializeAuth();
  }, [token, getCurrentUser, logout]);

  if (!isInitialized) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          backgroundColor: '#f0f2f5',
        }}
      >
        <Spin size="large" tip="Initializing..." />
      </div>
    );
  }

  return <>{children}</>;
};

export default AuthInitializer;
