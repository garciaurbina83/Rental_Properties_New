export interface AuditFields {
  created_at: string;
  updated_at: string;
  created_by: number;
  updated_by: number;
}

export interface BaseResponse {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}
