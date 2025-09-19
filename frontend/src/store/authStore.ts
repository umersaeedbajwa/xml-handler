import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import api from '../services/api';
import type { UserLogin, Token, UserDetails, ChangePasswordRequest } from '../types';

interface AuthState {
  user: UserDetails | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (credentials: UserLogin) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  changePassword: (data: ChangePasswordRequest) => Promise<void>;
  getCurrentUser: () => Promise<void>;
  setUser: (user: UserDetails | null) => void;
  setToken: (token: string | null) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

type AuthStore = AuthState & AuthActions;

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('authToken'),
  isAuthenticated: !!localStorage.getItem('authToken'),
  loading: false,
  error: null,
};

export const useAuthStore = create<AuthStore>()(
  devtools(
    (set) => ({
      ...initialState,
      
      login: async (credentials: UserLogin) => {
        try {
          set({ loading: true, error: null });
          
          const response = await api.post<Token>('/auth/login', credentials);
          const { access_token, user } = response.data;
          
          localStorage.setItem('authToken', access_token);
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            loading: false,
          });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Login failed',
            loading: false,
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          set({ loading: true });
          
          // Call logout endpoint
          await api.post('/auth/logout');
          
          localStorage.removeItem('authToken');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            loading: false,
            error: null,
          });
        } catch (error: any) {
          // Even if logout fails, clear local state
          localStorage.removeItem('authToken');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            loading: false,
            error: null,
          });
        }
      },

      // ...existing code...
      refreshToken: async () => {
        try {
          set({ loading: true });
          
          const response = await api.post<Token>('/auth/refresh');
          const { access_token } = response.data;
          
          localStorage.setItem('authToken', access_token);
          set({
            token: access_token,
            loading: false,
          });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Token refresh failed',
            loading: false,
          });
          throw error;
        }
      },

      changePassword: async (data: ChangePasswordRequest) => {
        try {
          set({ loading: true, error: null });
          
          await api.post('/auth/change-password', data);
          
          set({ loading: false });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Password change failed',
            loading: false,
          });
          throw error;
        }
      },

      getCurrentUser: async () => {
        try {
          set({ loading: true });
          
          const response = await api.get<UserDetails>('/auth/user-details');
          
          set({
            user: response.data,
            isAuthenticated: true,
            loading: false,
          });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Failed to get user details',
            loading: false,
          });
          throw error;
        }
      },

      setUser: (user: UserDetails | null) => {
        set({ user, isAuthenticated: !!user });
      },

      setToken: (token: string | null) => {
        set({ token });
        if (token) {
          localStorage.setItem('authToken', token);
        } else {
          localStorage.removeItem('authToken');
        }
      },

      setError: (error: string | null) => {
        set({ error });
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-store',
    }
  )
);
