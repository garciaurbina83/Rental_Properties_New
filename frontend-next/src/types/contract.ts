import { BaseResponse } from './common';

export enum ContractStatus {
  DRAFT = 'DRAFT',
  ACTIVE = 'ACTIVE',
  EXPIRED = 'EXPIRED',
  TERMINATED = 'TERMINATED'
}

export interface Contract extends BaseResponse {
  property_id: number;
  unit_id: number;
  tenant_id: number;
  start_date: string;
  end_date: string;
  rent_amount: number;
  deposit_amount: number;
  status: ContractStatus;
  payment_day: number;
  terms: string;
  notes?: string;
}

export interface ContractCreate {
  property_id: number;
  unit_id: number;
  tenant_id: number;
  start_date: string;
  end_date: string;
  rent_amount: number;
  deposit_amount: number;
  payment_day: number;
  terms: string;
  notes?: string;
}

export interface ContractUpdate {
  start_date?: string;
  end_date?: string;
  rent_amount?: number;
  deposit_amount?: number;
  status?: ContractStatus;
  payment_day?: number;
  terms?: string;
  notes?: string;
}

export interface ContractDocument extends BaseResponse {
  contract_id: number;
  document_type: string;
  file_name: string;
  file_path: string;
  description?: string;
}
