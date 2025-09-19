import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../services/api';

export interface Tenant {
  tenant_id: number;
  tenant_name: string;
  description?: string;
}

interface TenantState {
  tenants: Tenant[];
  selectedTenant: Tenant | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchTenants: () => Promise<void>;
  setSelectedTenant: (tenant: Tenant) => void;
  clearSelectedTenant: () => void;
}

export const useTenantStore = create<TenantState>()(
  persist(
    (set) => ({
      tenants: [],
      selectedTenant: null,
      loading: false,
      error: null,

      fetchTenants: async () => {
        set({ loading: true, error: null });
        try {
          const response = await api.get('/api/tenants/');
          set({ tenants: response.data, loading: false });
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Failed to fetch tenants',
            loading: false 
          });
          throw error;
        }
      },

      setSelectedTenant: (tenant: Tenant) => {
        set({ selectedTenant: tenant });
        // Store in localStorage for the interceptor
        localStorage.setItem('selectedTenantId', tenant.tenant_id.toString());
      },

      clearSelectedTenant: () => {
        set({ selectedTenant: null });
        localStorage.removeItem('selectedTenantId');
      },
    }),
    {
      name: 'tenant-storage',
      partialize: (state) => ({ 
        selectedTenant: state.selectedTenant 
      }),
    }
  )
);
