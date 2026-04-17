import { apiClient } from "@/lib/api/client";
import type { JwtAuthResponse } from "@/types/api";

import type { RefreshTokenInput } from "@/features/users/types/auth";

export async function refreshAccessToken(
  payload: RefreshTokenInput,
): Promise<Pick<JwtAuthResponse, "access">> {
  return apiClient.post<Pick<JwtAuthResponse, "access">>("/users/token/refresh/", payload);
}