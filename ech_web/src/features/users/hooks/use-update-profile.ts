"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateUserProfile } from "@/features/users/api/profile";
import type { ProfileSchemaValues } from "@/features/users/schemas/profile-schema";
import { useAuth } from "@/providers/auth-provider";

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const { refreshProfile } = useAuth();

  return useMutation({
    mutationFn: async (payload: Partial<ProfileSchemaValues>) => {
      return updateUserProfile(payload);
    },

    onSuccess: (updatedProfile) => {
      refreshProfile(updatedProfile);

      queryClient.setQueryData(["users", "profile"], updatedProfile);
      queryClient.invalidateQueries({ queryKey: ["users", "profile"] });
    },
  });
}