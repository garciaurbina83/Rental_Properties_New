import { BaseResponse } from './common';

export enum PropertyType {
  MAIN = "Main",
  UNIT = "Unit"
}

export enum PropertyStatus {
  AVAILABLE = "available",
  RENTED = "rented",
  MAINTENANCE = "maintenance",
  UNAVAILABLE = "unavailable"
}

export interface Property {
  id: number;
  name: string;
  property_type: PropertyType;
  status: PropertyStatus;
  parent_id?: number;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  country?: string;
  latitude?: number;
  longitude?: number;
  bedrooms?: number;
  bathrooms?: number;
  parking_spots?: number;
  year_built?: number;
  purchase_price?: number;
  monthly_rent?: number;
  documents?: Record<string, any>;
  notes?: string;
  images?: Record<string, any>;
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
}

export interface PropertyCreate {
  name: string;
  property_type: PropertyType;
  parent_id?: number;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  country?: string;
  latitude?: number;
  longitude?: number;
  bedrooms?: number;
  bathrooms?: number;
  parking_spots?: number;
  year_built?: number;
  purchase_price?: number;
  monthly_rent?: number;
  documents?: Record<string, any>;
  notes?: string;
  images?: Record<string, any>;
}

export interface PropertyUpdate extends Partial<PropertyCreate> {
  status?: PropertyStatus;
}
