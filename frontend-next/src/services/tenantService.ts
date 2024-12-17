import axios from 'axios';
import { Tenant, TenantFormData } from '@/app/tenants/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('🚀 Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      params: config.params,
      data: config.data,
      headers: config.headers,
    });
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log('✅ Response:', {
      status: response.status,
      data: response.data,
      headers: response.headers,
    });
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
    });
    return Promise.reject(error);
  }
);

export const tenantService = {
  async getTenants(params?: any): Promise<Tenant[]> {
    try {
      const response = await api.get('/tenants', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching tenants:', error);
      throw error;
    }
  },

  async getTenant(id: number): Promise<Tenant> {
    try {
      const response = await api.get(`/tenants/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching tenant ${id}:`, error);
      throw error;
    }
  },

  async createTenant(tenant: TenantFormData): Promise<Tenant> {
    try {
      const response = await api.post('/tenants', tenant);
      return response.data;
    } catch (error) {
      console.error('Error creating tenant:', error);
      throw error;
    }
  },

  async updateTenant(id: number, tenant: Partial<TenantFormData>): Promise<Tenant> {
    try {
      const response = await api.put(`/tenants/${id}`, tenant);
      return response.data;
    } catch (error) {
      console.error(`Error updating tenant ${id}:`, error);
      throw error;
    }
  },

  async deleteTenant(id: number): Promise<void> {
    try {
      await api.delete(`/tenants/${id}`);
    } catch (error) {
      console.error(`Error deleting tenant ${id}:`, error);
      throw error;
    }
  },

  async searchTenants(searchTerm: string, params?: any): Promise<Tenant[]> {
    try {
      const response = await api.get('/tenants/search', {
        params: {
          q: searchTerm,
          ...params,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error searching tenants:', error);
      throw error;
    }
  },
};
