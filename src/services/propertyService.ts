import axios from 'axios';
import { Property, PropertyCreate, PropertyType, PropertyStatus } from '@/types/property';

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

export const propertyService = {
  async getProperties(skip = 0, limit = 10, filters = {}) {
    try {
      const params = {
        skip,
        limit,
        ...filters,
      };

      const response = await api.get('/properties', { 
        params,
        timeout: 5000, // 5 second timeout
      });

      // Validar la respuesta
      if (!response.data) {
        throw new Error('No data received from API');
      }

      // Asegurar que la respuesta es un array
      const properties = Array.isArray(response.data) ? response.data : 
                        Array.isArray(response.data.items) ? response.data.items : 
                        [];

      return properties;
    } catch (error: any) {
      console.error('Error in getProperties:', error);
      
      if (error.code === 'ECONNREFUSED') {
        throw new Error('Could not connect to the API. Please check if the backend server is running.');
      }
      
      if (error.response) {
        throw new Error(`Server error: ${error.response.status} - ${error.response.data?.detail || error.message}`);
      } else if (error.request) {
        throw new Error('No response received from server. Please check if the backend is running.');
      } else {
        throw new Error(`Error making request: ${error.message}`);
      }
    }
  },

  async getProperty(id: number) {
    try {
      console.log('Making request to:', `${API_URL}/api/v1/properties/${id}`);

      const response = await api.get(`/properties/${id}`);

      if (!response.data) {
        throw new Error('No data received from API');
      }

      return response.data;
    } catch (error: any) {
      console.error('Error in getProperty:', error);
      if (error.response) {
        throw new Error(`Server error: ${error.response.status} - ${error.response.data?.detail || error.message}`);
      } else if (error.request) {
        throw new Error('No response received from server. Please check if the backend is running.');
      } else {
        throw new Error(`Error making request: ${error.message}`);
      }
    }
  },

  async createProperty(property: PropertyCreate) {
    try {
      console.log('Creating property with data:', property);
      
      if (property.property_type === PropertyType.UNIT && !property.parent_id) {
        throw new Error('Units must have a parent property');
      }

      // Convert property_type to the expected format
      const propertyData = {
        ...property,
        property_type: property.property_type,
        status: PropertyStatus.AVAILABLE,
      };

      console.log('Sending formatted data to API:', JSON.stringify(propertyData, null, 2));
      
      const response = await api.post('/properties', propertyData);

      if (!response.data) {
        throw new Error('No data received from API');
      }

      return response.data;
    } catch (error: any) {
      console.error('Error in createProperty:', error);
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw error;
    }
  },

  async updateProperty(id: number, property: any) {
    try {
      console.log('Making request to:', `${API_URL}/api/v1/properties/${id}`);
      console.log('With data:', property);

      const response = await api.put(`/properties/${id}`, property);

      if (!response.data) {
        throw new Error('No data received from API');
      }

      return response.data;
    } catch (error: any) {
      console.error('Error in updateProperty:', error);
      if (error.response) {
        throw new Error(`Server error: ${error.response.status} - ${error.response.data?.detail || error.message}`);
      } else if (error.request) {
        throw new Error('No response received from server. Please check if the backend is running.');
      } else {
        throw new Error(`Error making request: ${error.message}`);
      }
    }
  },

  async deleteProperty(id: number) {
    try {
      console.log('Making request to:', `${API_URL}/api/v1/properties/${id}`);

      await api.delete(`/properties/${id}`);
    } catch (error: any) {
      console.error('Error in deleteProperty:', error);
      if (error.response) {
        throw new Error(`Server error: ${error.response.status} - ${error.response.data?.detail || error.message}`);
      } else if (error.request) {
        throw new Error('No response received from server. Please check if the backend is running.');
      } else {
        throw new Error(`Error making request: ${error.message}`);
      }
    }
  },

  async searchProperties(searchTerm: string, params?: any) {
    try {
      console.log('Making request to:', `${API_URL}/api/v1/properties/search/${searchTerm}`);
      console.log('With params:', params);

      const response = await api.get(`/properties/search/${searchTerm}`, { params });

      if (!response.data) {
        throw new Error('No data received from API');
      }

      return response.data;
    } catch (error: any) {
      console.error('Error in searchProperties:', error);
      if (error.response) {
        throw new Error(`Server error: ${error.response.status} - ${error.response.data?.detail || error.message}`);
      } else if (error.request) {
        throw new Error('No response received from server. Please check if the backend is running.');
      } else {
        throw new Error(`Error making request: ${error.message}`);
      }
    }
  },
};
