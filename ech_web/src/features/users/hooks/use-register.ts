"use client";

import { useMutation } from "@tanstack/react-query";

import { registerUser } from "@/features/users/api/register";
import type { RegisterInput } from "@/features/users/types/auth";

export function useRegister() {
  return useMutation({
    mutationFn: (payload: RegisterInput) => registerUser(payload),
  });
}