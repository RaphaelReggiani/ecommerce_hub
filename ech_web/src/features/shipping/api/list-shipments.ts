import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type { PaginatedApiResponse } from "@/types/api";

import type {
  ShipmentFiltersInput,
  ShipmentListItem,
} from "@/features/shipping/types/shipment";

export async function listShipments(
  filters: ShipmentFiltersInput = {},
): Promise<PaginatedApiResponse<ShipmentListItem>> {
  const queryString = buildQueryString(filters);

  return apiClient.get<PaginatedApiResponse<ShipmentListItem>>(
    `/shipping/${queryString}`,
    { auth: true },
  );
}