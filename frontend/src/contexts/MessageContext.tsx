import React, { createContext, useContext, useEffect } from 'react';
import type { ReactNode } from 'react';
import { message } from 'antd';
import { initializeMessageService } from '../services/messageService';

interface MessageContextType {
  success: (content: string) => void;
  error: (content: string) => void;
  warning: (content: string) => void;
  info: (content: string) => void;
  loading: (options: { content: string; key?: string; duration?: number }) => void;
  destroy: (key?: string) => void;
}

const MessageContext = createContext<MessageContextType | null>(null);

export const MessageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [messageApi, contextHolder] = message.useMessage();

  const messageService: MessageContextType = {
    success: (content: string) => {
      messageApi.success(content);
    },
    error: (content: string) => {
      messageApi.error(content);
    },
    warning: (content: string) => {
      messageApi.warning(content);
    },
    info: (content: string) => {
      messageApi.info(content);
    },
    loading: (options: { content: string; key?: string; duration?: number }) => {
      messageApi.loading(options);
    },
    destroy: (key?: string) => {
      messageApi.destroy(key);
    }
  };

  // Initialize the global message service
  useEffect(() => {
    initializeMessageService(messageService);
  }, []);

  return (
    <MessageContext.Provider value={messageService}>
      {contextHolder}
      {children}
    </MessageContext.Provider>
  );
};

export const useMessage = () => {
  const context = useContext(MessageContext);
  if (!context) {
    throw new Error('useMessage must be used within a MessageProvider');
  }
  return context;
};
