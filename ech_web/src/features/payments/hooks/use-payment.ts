"use client";

import { useQuery } from "@tanstack/react-query";

import { retrievePayment } from "@/features/payments/api/retrieve-payment";
import { paymentQueryKeys } from "@/features/payments/utils/payment-query-keys";

export function usePayment(paymentId?: string) {
  return useQuery({
    queryKey: paymentQueryKeys.detail(paymentId ?? ""),
    queryFn: () => {
      if (!paymentId) {
        throw new Error("Payment id is required");
      }

      return retrievePayment(paymentId);
    },
    enabled: Boolean(paymentId),
  });
}