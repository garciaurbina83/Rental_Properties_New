import { BaseResponse } from './common';

export enum PaymentStatus {
  PENDING = 'PENDING',
  PAID = 'PAID',
  LATE = 'LATE',
  CANCELLED = 'CANCELLED'
}

export enum PaymentType {
  RENT = 'RENT',
  DEPOSIT = 'DEPOSIT',
  LATE_FEE = 'LATE_FEE',
  UTILITY = 'UTILITY',
  OTHER = 'OTHER'
}

export interface Payment extends BaseResponse {
  contract_id: number;
  amount: number;
  due_date: string;
  payment_date?: string;
  status: PaymentStatus;
  payment_type: PaymentType;
  reference_number?: string;
  notes?: string;
  late_fee?: number;
}

export interface PaymentCreate {
  contract_id: number;
  amount: number;
  due_date: string;
  payment_type: PaymentType;
  reference_number?: string;
  notes?: string;
}

export interface PaymentUpdate {
  amount?: number;
  due_date?: string;
  payment_date?: string;
  status?: PaymentStatus;
  reference_number?: string;
  notes?: string;
  late_fee?: number;
}
