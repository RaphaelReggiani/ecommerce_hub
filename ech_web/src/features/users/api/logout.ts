import { apiClient } from "@/lib/api/client";
import type { ApiSuccessDetailResponse } from "@/types/api";

import type { LogoutInput } from "@/features/users/types/auth";

export async function logoutUser(payload: LogoutInput): Promise<ApiSuccessDetailResponse | void> {
  return apiClient.post<ApiSuccessDetailResponse | void>("/users/logout/", payload, {
    auth: true,
  });
}