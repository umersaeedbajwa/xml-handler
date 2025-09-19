import axios, { AxiosError } from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import { showSuccess, showError, showLoading, destroyMessage } from './messageService';

// Create axios instance with base configuration
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add tenant ID header if available
    const tenantId = localStorage.getItem('selectedTenantId');
    if (tenantId) {
      config.headers['X-Tenant-Id'] = tenantId;
    }
    
    // Show loading message for non-GET requests
    if (config.method !== 'get') {
      showLoading('Processing...', 'api-loading');
    }
    
    return config;
  },
  (error) => {
    destroyMessage('api-loading');
    showError('Request configuration error');
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Destroy loading message
    destroyMessage('api-loading');
    
    // Show success message for non-GET requests
    if (response.config.method !== 'get') {
      const method = response.config.method?.toUpperCase();
      let successMessage = 'Operation completed successfully';
      
      switch (method) {
        case 'POST':
          successMessage = 'Created successfully';
          break;
        case 'PUT':
        case 'PATCH':
          successMessage = 'Updated successfully';
          break;
        case 'DELETE':
          successMessage = 'Deleted successfully';
          break;
      }
      
      showSuccess(successMessage);
    }
    
    return response;
  },
  (error: AxiosError) => {
    // Destroy loading message
    destroyMessage('api-loading');
    
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          showError(
            (data as any)?.detail || 'Bad request. Please check your input.'
          );
          break;
        case 401:
          // showError('Unauthorized. Please login again.');
          // // Clear auth state and redirect to login
          // localStorage.removeItem('authToken');
          // // Redirect to login page
          // if (window.location.pathname !== '/login') {
          //   window.location.href = '/login';
          // }
          break;
        case 403:
          // showError('Forbidden. You do not have permission.');
          break;
        case 404:
          showError('Resource not found.');
          break;
        case 422:
          // Validation errors
          const detail = (data as any)?.detail;
          if (Array.isArray(detail)) {
            const errorMessages = detail.map((err: any) => 
              `${err.loc?.join('.')}: ${err.msg}`
            ).join(', ');
            showError(`Validation error: ${errorMessages}`);
          } else {
            showError(detail || 'Validation error occurred.');
          }
          break;
        case 500:
          showError('Internal server error. Please try again later.');
          break;
        default:
          showError(
            (data as any)?.detail || `Server error: ${status}`
          );
      }
    } else if (error.request) {
      // Network error
      showError('Network error. Please check your connection.');
    } else {
      // Other error
      showError('An unexpected error occurred.');
    }
    
    return Promise.reject(error);
  }
);

export default api;
