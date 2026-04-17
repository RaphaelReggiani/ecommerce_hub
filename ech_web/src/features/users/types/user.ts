export type SessionUserData = {
  id: number;
  email: string;
  user_name: string;
  role: string;
  is_active: boolean;
  email_confirmed: boolean;
};

export type ProfileData = {
  user_email: string;
  user_name: string;
  user_phone: string;
  user_country: string;
  user_state: string;
  user_address: string;
  user_age: number | null;
};