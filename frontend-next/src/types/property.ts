import { BaseResponse } from './common';

export enum PropertyType {
  PRINCIPAL = 'PRINCIPAL',
  UNIT = 'UNIT',
}

export enum PropertyStatus {
  AVAILABLE = 'available',
  RENTED = 'rented',
  MAINTENANCE = 'maintenance',
  UNAVAILABLE = 'unavailable',
}

export interface Property {
  id: number;
  name?: string;
  address: string;
  city?: string;
  state?: string;
  zip_code?: string;
  bedrooms?: number;
  bathrooms?: number;
  status: PropertyStatus;
  is_active: boolean;
  property_type: PropertyType;
  parent_property_id?: number | null;
  user_id: string;
  created_at?: string;
  updated_at?: string;
}

export interface PropertyCreate {
  name?: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  bedrooms: number;
  bathrooms: number;
  status?: PropertyStatus;
  is_active?: boolean;
  property_type: PropertyType;
  parent_property_id?: number | null;
}

export interface PropertyUpdate extends Partial<PropertyCreate> {}
