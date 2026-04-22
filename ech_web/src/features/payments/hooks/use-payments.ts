"use client";

import { useQuery } from "@tanstack/react-query";

import { listPayments } from "@/features/payments/api/list-payments";
import type { PaymentFiltersInput } from "@/features/payments/types/payment";
import { paymentQueryKeys } from "@/features/payments/utils/payment-query-keys";

export function usePayments(filters: PaymentFiltersInput = {}) {
  return useQuery({
    queryKey: paymentQueryKeys.list(filters),
    queryFn: () => listPayments(filters),
  });
}