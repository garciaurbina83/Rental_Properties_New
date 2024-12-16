import { BaseResponse } from './common';

export enum PropertyType {
  PRINCIPAL = 'PRINCIPAL',
  UNIT = 'UNIT',
}

export enum PropertyStatus {
  AVAILABLE = 'available',
  RENTED = 'rented',
}

export interface Property {
  id: number;
  name?: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  bedrooms: number;
  bathrooms: number;
  status: PropertyStatus;
  is_active: boolean;
  property_type: PropertyType;
  parent_property_id?: number;
  created_at: string;
  updated_at: string;
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
  parent_property_id?: number;
}

export interface PropertyUpdate extends Partial<PropertyCreate> {}
