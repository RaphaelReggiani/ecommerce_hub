import type { PaymentFiltersInput } from "@/features/payments/types/payment";

export const paymentQueryKeys = {
  all: ["payments"] as const,

  lists: () => [...paymentQueryKeys.all, "list"] as const,

  list: (filters: PaymentFiltersInput = {}) =>
    [...paymentQueryKeys.lists(), filters] as const,

  details: () => [...paymentQueryKeys.all, "detail"] as const,

  detail: (paymentId: string) =>
    [...paymentQueryKeys.details(), paymentId] as const,

  managementDetails: () => [...paymentQueryKeys.all, "management", "detail"] as const,

  managementDetail: (paymentId: string) =>
    [...paymentQueryKeys.managementDetails(), paymentId] as const,

  transactions: (paymentId: string) =>
    [...paymentQueryKeys.all, "transactions", paymentId] as const,

  refunds: (paymentId: string) =>
    [...paymentQueryKeys.all, "refunds", paymentId] as const,
};