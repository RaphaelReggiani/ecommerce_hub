"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createPayment } from "@/features/payments/api/create-payment";
import type { CreatePaymentInput } from "@/features/payments/types/payment";
import { paymentQueryKeys } from "@/features/payments/utils/payment-query-keys";

export function useCreatePayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreatePaymentInput) => createPayment(payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: paymentQueryKeys.lists(),
      });
    },
  });
}