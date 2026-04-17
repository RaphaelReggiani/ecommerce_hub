"use client";

import { useMutation } from "@tanstack/react-query";

import { logoutUser } from "@/features/users/api/logout";
import { getRefreshToken } from "@/lib/auth/auth-session";
import { useAuth } from "@/providers/auth-provider";

export function useLogout() {
  const { logout } = useAuth();

  return useMutation({
    mutationFn: async () => {
      const refresh = getRefreshToken();

      if (!refresh) {
        logout();
        return;
      }

      await logoutUser({ refresh });
      logout();
    },
  });
}