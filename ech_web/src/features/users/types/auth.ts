export type LoginInput = {
  email: string;
  password: string;
};

export type RegisterInput = {
  email: string;
  password: string;
  user_name: string;
};

export type LogoutInput = {
  refresh: string;
};

export type RefreshTokenInput = {
  refresh: string;
};

export type ForgotPasswordInput = {
  email: string;
};

export type ResetPasswordInput = {
  token: string;
  new_password: string;
};