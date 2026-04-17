import { apiClient } from "@/lib/api/client";
import type { UserProfileResponse } from "@/types/api";

import type { ProfileSchemaValues } from "@/features/users/schemas/profile-schema";

export async function getUserProfile(): Promise<UserProfileResponse> {
  return apiClient.get<UserProfileResponse>("/users/profile/", {
    auth: true,
  });
}

export async function updateUserProfile(
  payload: Partial<ProfileSchemaValues>,
): Promise<UserProfileResponse> {
  return apiClient.patch<UserProfileResponse>("/users/profile/", payload, {
    auth: true,
  });
}