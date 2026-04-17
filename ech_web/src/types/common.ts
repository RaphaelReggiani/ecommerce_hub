export type ID = string | number;

export type Nullable<T> = T | null;
export type Maybe<T> = T | null | undefined;

export type Option = {
  label: string;
  value: string;
};

export type LabelValue = {
  label: string;
  value: string | number;
};

export type BaseEntity = {
  id: ID;
  created_at?: string;
  updated_at?: string;
};

export type SessionUser = {
  id: number;
  email: string;
  user_name: string;
  role: string;
  is_active: boolean;
  email_confirmed: boolean;
};

export type UserProfile = {
  user_email: string;
  user_name: string;
  user_phone: string;
  user_country: string;
  user_state: string;
  user_address: string;
  user_age: number | null;
};