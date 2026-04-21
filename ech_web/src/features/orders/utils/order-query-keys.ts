import type { OrderStatus, PaymentStatus, ShippingStatus } from "@/features/orders/types/order";

type OrderFilters = {
  status?: OrderStatus;
  payment_status?: PaymentStatus;
  shipping_status?: ShippingStatus;
  customer_email?: string;
  customer_name?: string;
  created_after?: string;
  created_before?: string;
  page?: number;
};

export const orderQueryKeys = {
  all: ["orders"] as const,
  list: (filters: OrderFilters = {}) => ["orders", "list", filters] as const,
  detail: (orderId: string) => ["orders", "detail", orderId] as const,

  managementList: (filters: OrderFilters = {}) =>
    ["orders", "management", "list", filters] as const,

  managementDetail: (orderId: string) =>
    ["orders", "management", "detail", orderId] as const,

  cart: ["orders", "cart"] as const,
};