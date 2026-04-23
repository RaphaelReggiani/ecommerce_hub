"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { loginUser } from "@/features/users/api/login";
import { getCurrentUser } from "@/features/users/api/me";
import type { LoginInput } from "@/features/users/types/auth";
import { mapApiUserToSessionUser } from "@/features/users/utils/auth-mappers";
import { useAuth } from "@/providers/auth-provider";
import { routes } from "@/config/routes";

export function useLogin() {
  const { setSession } = useAuth();
  const router = useRouter();

  return useMutation({
    mutationFn: async (payload: LoginInput) => {
      const tokens = await loginUser(payload);
      const user = await getCurrentUser(tokens.access);

      return {
        tokens,
        user,
      };
    },

    onSuccess: ({ tokens, user }) => {
      const sessionUser = mapApiUserToSessionUser(user);

      setSession(tokens, sessionUser);
      router.replace(routes.protected.account);
    },
  });
}