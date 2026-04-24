import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type {
  AnalyticsPeriodFilters,
  CustomerSummary,
} from "@/features/analytics/types/analytics";

export async function getCustomerSummary(
  filters: AnalyticsPeriodFilters,
): Promise<CustomerSummary> {
  const queryString = buildQueryString(filters);

  return apiClient.get<CustomerSummary>(
    `/analytics/customers/${queryString}`,
    { auth: true },
  );
}