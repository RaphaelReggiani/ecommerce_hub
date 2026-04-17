export type ApiDetailResponse = {
  detail?: string;
  message?: string;
};

export type ApiFieldErrors = Record<string, string[] | string>;

export type ApiErrorResponse = ApiDetailResponse & {
  status?: number;
  errors?: ApiFieldErrors;
  [key: string]: unknown;
};

export type PaginatedApiResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type JwtAuthResponse = {
  refresh: string;
  access: string;
};

export type UserOutputResponse = {
  id: number;
  email: string;
  user_name: string;
  role: string;
  is_active: boolean;
  email_confirmed: boolean;
};

export type UserProfileResponse = {
  user_email: string;
  user_name: string;
  user_phone: string;
  user_country: string;
  user_state: string;
  user_address: string;
  user_age: number | null;
};

export type ApiSuccessDetailResponse = {
  detail: string;
};