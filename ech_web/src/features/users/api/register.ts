import { apiClient } from "@/lib/api/client";
import { buildIdempotencyHeaders } from "@/lib/api/idempotency";
import type { UserOutputResponse } from "@/types/api";

import type { RegisterInput } from "@/features/users/types/auth";

export async function registerUser(payload: RegisterInput): Promise<UserOutputResponse> {
  return apiClient.post<UserOutputResponse>("/users/register/", payload, {
    headers: buildIdempotencyHeaders("users-register"),
  });
}