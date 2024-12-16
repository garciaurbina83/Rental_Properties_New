import { BaseResponse } from './common';

export enum TicketStatus {
  OPEN = 'OPEN',
  IN_PROGRESS = 'IN_PROGRESS',
  CLOSED = 'CLOSED',
  CANCELLED = 'CANCELLED'
}

export enum TicketPriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  URGENT = 'URGENT'
}

export interface MaintenanceTicket extends BaseResponse {
  property_id: number;
  unit_id?: number;
  tenant_id?: number;
  title: string;
  description: string;
  priority: TicketPriority;
  status: TicketStatus;
  scheduled_date?: string;
  completed_date?: string;
  resolution_notes?: string;
  cost?: number;
  vendor_id?: number;
}

export interface MaintenanceTicketCreate {
  property_id: number;
  unit_id?: number;
  tenant_id?: number;
  title: string;
  description: string;
  priority: TicketPriority;
  scheduled_date?: string;
  vendor_id?: number;
}

export interface MaintenanceTicketUpdate {
  title?: string;
  description?: string;
  priority?: TicketPriority;
  status?: TicketStatus;
  scheduled_date?: string;
  completed_date?: string;
  resolution_notes?: string;
  cost?: number;
  vendor_id?: number;
}
