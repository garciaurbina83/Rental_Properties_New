export interface Tenant {
  id: number
  first_name: string
  last_name: string
  property_id: number
  lease_start: string
  lease_end: string
  deposit: string
  monthly_rent: string
  payment_day: number
  created_at: string
  updated_at: string
}

export interface TenantFormData {
  first_name: string
  last_name: string
  property_id: number
  lease_start: Date
  lease_end: Date
  deposit: number
  monthly_rent: number
  payment_day: number
}
