import axios from 'axios';
import { Property, PropertyCreate, PropertyType, PropertyStatus } from '@/types/property';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true, // Importante para CORS
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
      headers: error.response?.headers,
    });
    return Promise.reject(error);
  }
);

export const propertyService = {
  async getProperties(params?: any): Promise<Property[]> {
    try {
      const response = await api.get('/properties', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching properties:', error);
      throw error;
    }
  },

  async getProperty(id: number): Promise<Property> {
    try {
      const response = await api.get(`/properties/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching property ${id}:`, error);
      throw error;
    }
  },

  async createProperty(property: PropertyCreate): Promise<Property> {
    try {
      // Asegurar que todos los campos requeridos estén presentes y con el tipo correcto
      const propertyData = {
        name: property.name || '',
        address: property.address || '',
        city: property.city || '',
        state: property.state || '',
        zip_code: property.zip_code || '',
        property_type: property.property_type || PropertyType.PRINCIPAL,
        bedrooms: Number(property.bedrooms || 0),
        bathrooms: Number(property.bathrooms || 0),
        status: property.status || PropertyStatus.AVAILABLE,
        is_active: property.is_active ?? true,
        parent_property_id: property.parent_property_id || null,
      };

      console.log('Creating property with data:', propertyData);
      const response = await api.post('/properties', propertyData);
      console.log('Property created successfully:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error creating property:', {
        error,
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      });
      throw error;
    }
  },

  async updateProperty(id: number, property: Partial<PropertyCreate>): Promise<Property> {
    try {
      const response = await api.put(`/properties/${id}`, property);
      return response.data;
    } catch (error) {
      console.error(`Error updating property ${id}:`, error);
      throw error;
    }
  },

  async deleteProperty(id: number): Promise<void> {
    try {
      await api.delete(`/properties/${id}`);
    } catch (error) {
      console.error(`Error deleting property ${id}:`, error);
      throw error;
    }
  },

  async searchProperties(searchTerm: string, params?: any): Promise<Property[]> {
    try {
      const response = await api.get('/properties/search', {
        params: {
          ...params,
          q: searchTerm,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error searching properties:', error);
      throw error;
    }
  },
};
