import { apiClient } from "@/lib/api/client";
import type { UserOutputResponse } from "@/types/api";

export async function getCurrentUser(accessToken?: string): Promise<UserOutputResponse> {
  return apiClient.get<UserOutputResponse>("/users/me/", {
    auth: !accessToken,
    accessToken,
  });
}