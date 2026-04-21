import { apiClient } from "@/lib/api/client";
import type { PaginatedApiResponse } from "@/types/api";
import type {
  OrderListItem,
  OrderStatus,
  PaymentStatus,
  ShippingStatus,
} from "@/features/orders/types/order";
import { buildQueryString } from "@/lib/utils/build-query-string";

export type ListOrdersFilters = {
  status?: OrderStatus;
  payment_status?: PaymentStatus;
  shipping_status?: ShippingStatus;
  page?: number;
};

export async function listOrders(
  filters: ListOrdersFilters = {},
): Promise<PaginatedApiResponse<OrderListItem>> {
  const queryString = buildQueryString(filters);

  return apiClient.get<PaginatedApiResponse<OrderListItem>>(
    `/orders/${queryString}`,
  );
}