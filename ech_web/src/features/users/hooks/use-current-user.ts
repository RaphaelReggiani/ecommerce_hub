"use client";

import { useQuery } from "@tanstack/react-query";

import { getCurrentUser } from "@/features/users/api/me";
import { useAuth } from "@/providers/auth-provider";

export function useCurrentUser() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ["users", "current-user"],
    queryFn: () => getCurrentUser(),
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 5,
  });
}