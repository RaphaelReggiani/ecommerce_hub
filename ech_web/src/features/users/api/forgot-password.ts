import { apiClient } from "@/lib/api/client";
import type { ApiSuccessDetailResponse } from "@/types/api";

import type { ForgotPasswordInput } from "@/features/users/types/auth";

export async function requestPasswordReset(
  payload: ForgotPasswordInput,
): Promise<ApiSuccessDetailResponse> {
  return apiClient.post<ApiSuccessDetailResponse>("/users/password-reset/", payload);
}