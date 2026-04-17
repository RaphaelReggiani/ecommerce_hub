import { apiClient } from "@/lib/api/client";
import type { JwtAuthResponse } from "@/types/api";

import type { LoginInput } from "@/features/users/types/auth";

export async function loginUser(payload: LoginInput): Promise<JwtAuthResponse> {
  return apiClient.post<JwtAuthResponse>("/users/login/", payload);
}