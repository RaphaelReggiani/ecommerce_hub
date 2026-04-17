import { apiClient } from "@/lib/api/client";
import type { ApiSuccessDetailResponse } from "@/types/api";

import type { ResetPasswordInput } from "@/features/users/types/auth";

export async function confirmPasswordReset(
  payload: ResetPasswordInput,
): Promise<ApiSuccessDetailResponse> {
  return apiClient.post<ApiSuccessDetailResponse>("/users/password-reset-confirm/", payload);
}