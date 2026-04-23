import { apiClient } from "@/lib/api/client";
import type { SessionUser } from "@/types/common";

export async function getCurrentUser(
  accessToken?: string,
): Promise<SessionUser> {
  return apiClient.get<SessionUser>("/users/me/", {
    auth: !accessToken,
    accessToken,
  });
}