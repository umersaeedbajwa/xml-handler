// Global message service that can be used anywhere
let messageService: any = null;

// Initialize the message service (called from MessageProvider)
export const initializeMessageService = (service: any) => {
  messageService = service;
};

// Message functions that can be used in non-React contexts
export const showSuccess = (content: string) => {
  if (messageService) {
    messageService.success(content);
  } else {
    console.log('Success:', content);
  }
};

export const showError = (content: string) => {
  if (messageService) {
    messageService.error(content);
  } else {
    console.error('Error:', content);
  }
};

export const showWarning = (content: string) => {
  if (messageService) {
    messageService.warning(content);
  } else {
    console.warn('Warning:', content);
  }
};

export const showInfo = (content: string) => {
  if (messageService) {
    messageService.info(content);
  } else {
    console.info('Info:', content);
  }
};

export const showLoading = (content: string, key?: string) => {
  if (messageService) {
    messageService.loading({ content, key, duration: 0 });
  } else {
    console.log('Loading:', content);
  }
};

export const destroyMessage = (key?: string) => {
  if (messageService) {
    messageService.destroy(key);
  }
};
