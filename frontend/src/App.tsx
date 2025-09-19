import React from 'react';
import { App as AntdApp, ConfigProvider } from 'antd';
import { MessageProvider } from './contexts/MessageContext';
import { AuthInitializer } from './components';
import AppRouter from './AppRouter';
import './App.css';

const App: React.FC = () => {
  return (
    <ConfigProvider>
      <AntdApp>
        <MessageProvider>
          <AuthInitializer>
            <AppRouter />
          </AuthInitializer>
        </MessageProvider>
      </AntdApp>
    </ConfigProvider>
  );
};

export default App;
