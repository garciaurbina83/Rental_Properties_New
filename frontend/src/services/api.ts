import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const propertyApi = {
  getProperties: () => api.get('/properties'),
  getProperty: (id: string) => api.get(`/properties/${id}`),
  createProperty: (data: any) => api.post('/properties', data),
  updateProperty: (id: string, data: any) => api.put(`/properties/${id}`, data),
  deleteProperty: (id: string) => api.delete(`/properties/${id}`),
};

export const tenantApi = {
  getTenants: () => api.get('/tenants'),
  getTenant: (id: string) => api.get(`/tenants/${id}`),
  createTenant: (data: any) => api.post('/tenants', data),
  updateTenant: (id: string, data: any) => api.put(`/tenants/${id}`, data),
  deleteTenant: (id: string) => api.delete(`/tenants/${id}`),
};

export const leaseApi = {
  getLeases: () => api.get('/leases'),
  getLease: (id: string) => api.get(`/leases/${id}`),
  createLease: (data: any) => api.post('/leases', data),
  updateLease: (id: string, data: any) => api.put(`/leases/${id}`, data),
  deleteLease: (id: string) => api.delete(`/leases/${id}`),
};

export default api;
