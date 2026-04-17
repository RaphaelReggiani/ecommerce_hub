"use client";

import { useQuery } from "@tanstack/react-query";

import { getUserProfile } from "@/features/users/api/profile";
import { useAuth } from "@/providers/auth-provider";

export function useProfile() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ["users", "profile"],
    queryFn: () => getUserProfile(),
    enabled: isAuthenticated,
  });
}