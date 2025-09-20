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
  getAll: (): Promise<Domain[]> => 
    api.get(`${BASE_URL}/domains`),
  
  getById: (id: string): Promise<Domain> => 
    api.get(`${BASE_URL}/domains/${id}`),
  
  create: (data: DomainCreate): Promise<Domain> => 
    api.post(`${BASE_URL}/domains`, data),
  
  update: (id: string, data: DomainUpdate): Promise<Domain> => 
    api.put(`${BASE_URL}/domains/${id}`, data),
  
  delete: (id: string): Promise<void> => 
    api.delete(`${BASE_URL}/domains/${id}`)
};

// Contact API
export const contactApi = {
  getAll: (): Promise<Contact[]> => 
    api.get(`${BASE_URL}/contacts`),
  
  getById: (id: string): Promise<Contact> => 
    api.get(`${BASE_URL}/contacts/${id}`),
  
  create: (data: ContactCreate): Promise<Contact> => 
    api.post(`${BASE_URL}/contacts`, data),
  
  update: (id: string, data: ContactUpdate): Promise<Contact> => 
    api.put(`${BASE_URL}/contacts/${id}`, data),
  
  delete: (id: string): Promise<void> => 
    api.delete(`${BASE_URL}/contacts/${id}`)
};

// User API
export const userApi = {
  getAll: (): Promise<User[]> => 
    api.get(`${BASE_URL}/users`),
  
  getById: (id: string): Promise<User> => 
    api.get(`${BASE_URL}/users/${id}`),
  
  create: (data: UserCreate): Promise<User> => 
    api.post(`${BASE_URL}/users`, data),
  
  update: (id: string, data: UserUpdate): Promise<User> => 
    api.put(`${BASE_URL}/users/${id}`, data),
  
  delete: (id: string): Promise<void> => 
    api.delete(`${BASE_URL}/users/${id}`)
};

// Extension API
export const extensionApi = {
  getAll: (): Promise<Extension[]> => 
    api.get(`${BASE_URL}/extensions`),
  
  getById: (id: string): Promise<Extension> => 
    api.get(`${BASE_URL}/extensions/${id}`),
  
  create: (data: ExtensionCreate): Promise<Extension> => 
    api.post(`${BASE_URL}/extensions`, data),
  
  update: (id: string, data: Partial<ExtensionCreate>): Promise<Extension> => 
    api.put(`${BASE_URL}/extensions/${id}`, data),
  
  delete: (id: string): Promise<void> => 
    api.delete(`${BASE_URL}/extensions/${id}`)
};

// Extension Settings API
export const extensionSettingApi = {
  getAll: (): Promise<ExtensionSetting[]> => 
    api.get(`${BASE_URL}/extension-settings`),
  
  getByExtension: (extensionId: string): Promise<ExtensionSetting[]> => 
    api.get(`${BASE_URL}/extension-settings/extension/${extensionId}`),
  
  create: (data: ExtensionSettingCreate): Promise<ExtensionSetting> => 
    api.post(`${BASE_URL}/extension-settings`, data),
  
  update: (id: string, data: ExtensionSettingUpdate): Promise<ExtensionSetting> => 
    api.put(`${BASE_URL}/extension-settings/${id}`, data),
  
  delete: (id: string): Promise<void> => 
    api.delete(`${BASE_URL}/extension-settings/${id}`)
};

// Voicemail API
export const voicemailApi = {
  getAll: (): Promise<Voicemail[]> => 
    api.get(`${BASE_URL}/voicemails`),
  
  getById: (id: string): Promise<Voicemail> => 
    api.get(`${BASE_URL}/voicemails/${id}`),
  
  create: (data: VoicemailCreate): Promise<Voicemail> => 
    api.post(`${BASE_URL}/voicemails`, data),
  
  update: (id: string, data: VoicemailUpdate): Promise<Voicemail> => 
    api.put(`${BASE_URL}/voicemails/${id}`, data),
  
  delete: (id: string): Promise<void> => 
    api.delete(`${BASE_URL}/voicemails/${id}`)
};

// Dialplan API
export const dialplanApi = {
  getAll: (): Promise<Dialplan[]> => 
    api.get(`${BASE_URL}/dialplans`),
  
  getById: (id: string): Promise<Dialplan> => 
    api.get(`${BASE_URL}/dialplans/${id}`),
  
  create: (data: DialplanCreate): Promise<Dialplan> => 
    api.post(`${BASE_URL}/dialplans`, data),
  
  update: (id: string, data: DialplanUpdate): Promise<Dialplan> => 
    api.put(`${BASE_URL}/dialplans/${id}`, data),
  
  delete: (id: string): Promise<void> => 
    api.delete(`${BASE_URL}/dialplans/${id}`)
};

// Registration API (read-only)
export const registrationApi = {
  getAll: (): Promise<Registration[]> => 
    api.get(`${BASE_URL}/registrations`),
  
  getById: (id: string): Promise<Registration> => 
    api.get(`${BASE_URL}/registrations/${id}`)
};