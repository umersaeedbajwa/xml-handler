import api from './api';
import type {
  Domain, DomainCreate, DomainUpdate,
  Contact, ContactCreate, ContactUpdate,
  User, UserCreate, UserUpdate,
  Extension, ExtensionCreate, ExtensionSetting, ExtensionSettingCreate, ExtensionSettingUpdate,
  Voicemail, VoicemailCreate, VoicemailUpdate,
  Dialplan, DialplanCreate, DialplanUpdate,
  Registration
} from '../types/freeswitch';

const BASE_URL = '/api/freeswitch';

// Domain API
export const domainApi = {
  getAll: async (): Promise<Domain[]> => {
    const response = await api.get(`${BASE_URL}/domains`);
    return response.data;
  },
  
  getById: async (id: string): Promise<Domain> => {
    const response = await api.get(`${BASE_URL}/domains/${id}`);
    return response.data;
  },
  
  create: async (data: DomainCreate): Promise<Domain> => {
    const response = await api.post(`${BASE_URL}/domains`, data);
    return response.data;
  },
  
  update: async (id: string, data: DomainUpdate): Promise<Domain> => {
    const response = await api.put(`${BASE_URL}/domains/${id}`, data);
    return response.data;
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE_URL}/domains/${id}`);
  }
};

// Contact API
export const contactApi = {
  getAll: async (): Promise<Contact[]> => {
    const response = await api.get(`${BASE_URL}/contacts`);
    return response.data;
  },
  
  getById: async (id: string): Promise<Contact> => {
    const response = await api.get(`${BASE_URL}/contacts/${id}`);
    return response.data;
  },
  
  create: async (data: ContactCreate): Promise<Contact> => {
    const response = await api.post(`${BASE_URL}/contacts`, data);
    return response.data;
  },
  
  update: async (id: string, data: ContactUpdate): Promise<Contact> => {
    const response = await api.put(`${BASE_URL}/contacts/${id}`, data);
    return response.data;
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE_URL}/contacts/${id}`);
  }
};

// User API
export const userApi = {
  getAll: async (): Promise<User[]> => {
    const response = await api.get(`${BASE_URL}/users`);
    return response.data;
  },
  
  getById: async (id: string): Promise<User> => {
    const response = await api.get(`${BASE_URL}/users/${id}`);
    return response.data;
  },
  
  create: async (data: UserCreate): Promise<User> => {
    const response = await api.post(`${BASE_URL}/users`, data);
    return response.data;
  },
  
  update: async (id: string, data: UserUpdate): Promise<User> => {
    const response = await api.put(`${BASE_URL}/users/${id}`, data);
    return response.data;
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE_URL}/users/${id}`);
  }
};

// Extension API
export const extensionApi = {
  getAll: async (): Promise<Extension[]> => {
    const response = await api.get(`${BASE_URL}/extensions`);
    return response.data;
  },
  
  getById: async (id: string): Promise<Extension> => {
    const response = await api.get(`${BASE_URL}/extensions/${id}`);
    return response.data;
  },
  
  create: async (data: ExtensionCreate): Promise<Extension> => {
    const response = await api.post(`${BASE_URL}/extensions`, data);
    return response.data;
  },
  
  update: async (id: string, data: Partial<ExtensionCreate>): Promise<Extension> => {
    const response = await api.put(`${BASE_URL}/extensions/${id}`, data);
    return response.data;
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE_URL}/extensions/${id}`);
  }
};

// Extension Settings API
export const extensionSettingApi = {
  getAll: async (): Promise<ExtensionSetting[]> => {
    const response = await api.get(`${BASE_URL}/extension-settings`);
    return response.data;
  },
  
  getByExtension: async (extensionId: string): Promise<ExtensionSetting[]> => {
    const response = await api.get(`${BASE_URL}/extension-settings/extension/${extensionId}`);
    return response.data;
  },
  
  create: async (data: ExtensionSettingCreate): Promise<ExtensionSetting> => {
    const response = await api.post(`${BASE_URL}/extension-settings`, data);
    return response.data;
  },
  
  update: async (id: string, data: ExtensionSettingUpdate): Promise<ExtensionSetting> => {
    const response = await api.put(`${BASE_URL}/extension-settings/${id}`, data);
    return response.data;
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE_URL}/extension-settings/${id}`);
  }
};

// Voicemail API
export const voicemailApi = {
  getAll: async (): Promise<Voicemail[]> => {
    const response = await api.get(`${BASE_URL}/voicemails`);
    return response.data;
  },
  
  getById: async (id: string): Promise<Voicemail> => {
    const response = await api.get(`${BASE_URL}/voicemails/${id}`);
    return response.data;
  },
  
  create: async (data: VoicemailCreate): Promise<Voicemail> => {
    const response = await api.post(`${BASE_URL}/voicemails`, data);
    return response.data;
  },
  
  update: async (id: string, data: VoicemailUpdate): Promise<Voicemail> => {
    const response = await api.put(`${BASE_URL}/voicemails/${id}`, data);
    return response.data;
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE_URL}/voicemails/${id}`);
  }
};

// Dialplan API
export const dialplanApi = {
  getAll: async (): Promise<Dialplan[]> => {
    const response = await api.get(`${BASE_URL}/dialplans`);
    return response.data;
  },
  
  getById: async (id: string): Promise<Dialplan> => {
    const response = await api.get(`${BASE_URL}/dialplans/${id}`);
    return response.data;
  },
  
  create: async (data: DialplanCreate): Promise<Dialplan> => {
    const response = await api.post(`${BASE_URL}/dialplans`, data);
    return response.data;
  },
  
  update: async (id: string, data: DialplanUpdate): Promise<Dialplan> => {
    const response = await api.put(`${BASE_URL}/dialplans/${id}`, data);
    return response.data;
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE_URL}/dialplans/${id}`);
  }
};

// Registration API (read-only)
export const registrationApi = {
  getAll: async (): Promise<Registration[]> => {
    const response = await api.get(`${BASE_URL}/registrations`);
    return response.data;
  },
  
  getById: async (id: string): Promise<Registration> => {
    const response = await api.get(`${BASE_URL}/registrations/${id}`);
    return response.data;
  }
};