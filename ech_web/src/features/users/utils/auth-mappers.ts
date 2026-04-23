import type { SessionUser } from "@/types/common";

type ApiUserLike = {
  id?: number | string;
  email?: string;
  user_email?: string;
  user_name?: string;
  name?: string;
  role?: string;
  user_role?: string;
  is_active?: boolean;
  email_confirmed?: boolean;
};

export function mapApiUserToSessionUser(user: ApiUserLike): SessionUser {
  return {
    id: Number(user.id ?? 0),
    email: user.email ?? user.user_email ?? "",
    user_name: user.user_name ?? user.name ?? "",
    role: (user.role ?? user.user_role ?? "") as SessionUser["role"],
    is_active: Boolean(user.is_active),
    email_confirmed: Boolean(user.email_confirmed),
  };
}