import type { ReviewFiltersInput } from "@/features/reviews/types/review";

export const reviewQueryKeys = {
  all: ["reviews"] as const,

  lists: () => [...reviewQueryKeys.all, "list"] as const,

  list: (filters: ReviewFiltersInput = {}) =>
    [...reviewQueryKeys.lists(), filters] as const,

  details: () => [...reviewQueryKeys.all, "detail"] as const,

  detail: (reviewId: string) =>
    [...reviewQueryKeys.details(), reviewId] as const,

  productLists: () => [...reviewQueryKeys.all, "product", "list"] as const,

  productList: (productId: string, filters: ReviewFiltersInput = {}) =>
    [...reviewQueryKeys.productLists(), productId, filters] as const,

  productSummaries: () => [...reviewQueryKeys.all, "product", "summary"] as const,

  productSummary: (productId: string) =>
    [...reviewQueryKeys.productSummaries(), productId] as const,

  managementLists: () => [...reviewQueryKeys.all, "management", "list"] as const,

  managementList: (filters: ReviewFiltersInput = {}) =>
    [...reviewQueryKeys.managementLists(), filters] as const,

  managementDetails: () => [...reviewQueryKeys.all, "management", "detail"] as const,

  managementDetail: (reviewId: string) =>
    [...reviewQueryKeys.managementDetails(), reviewId] as const,
};