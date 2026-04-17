"use client";

import { useMutation } from "@tanstack/react-query";

import { loginUser } from "@/features/users/api/login";
import { getCurrentUser } from "@/features/users/api/me";
import type { LoginInput } from "@/features/users/types/auth";
import { useAuth } from "@/providers/auth-provider";

export function useLogin() {
  const { setSession } = useAuth();

  return useMutation({
    mutationFn: async (payload: LoginInput) => {
      const tokens = await loginUser(payload);
      const user = await getCurrentUser(tokens.access);

      setSession(tokens, {
        id: user.id,
        email: user.email,
        user_name: user.user_name,
        role: user.role,
        is_active: user.is_active,
        email_confirmed: user.email_confirmed,
      });

      return {
        tokens,
        user,
      };
    },
  });
}