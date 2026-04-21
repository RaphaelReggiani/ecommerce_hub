export type OrderStatus =
  | "pending"
  | "confirmed"
  | "processing"
  | "shipped"
  | "delivered"
  | "cancelled"
  | "refunded";

export type PaymentStatus =
  | "pending"
  | "processing"
  | "authorized"
  | "captured"
  | "failed"
  | "cancelled"
  | "partially_refunded"
  | "refunded";

export type ShippingStatus =
  | "pending"
  | "preparing"
  | "shipped"
  | "in_transit"
  | "delivered";

export type OrderItem = {
  id: string;
  product: string;
  product_name_snapshot: string;
  product_type_snapshot: string;
  brand_snapshot: string;
  quantity: number;
  unit_price: string;
  discount_price: string | null;
  total_price: string;
  created_at: string;
};

export type OrderTotals = {
  subtotal: string;
  discount_total: string;
  tax_total: string;
  shipping_total: string;
  grand_total: string;
  updated_at: string;
};

export type OrderAddress = {
  full_name: string;
  address_line: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  phone: string;
  created_at: string;
};

export type OrderEvent = {
  id: string;
  event_type: string;
  performed_by: number | null;
  performed_by_name: string | null;
  performed_by_email: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export type OrderNote = {
  id: string;
  author: number | null;
  author_name: string | null;
  author_email: string | null;
  message: string;
  is_internal: boolean;
  created_at: string;
};

export type OrderLifecycle = {
  confirmed_at: string | null;
  processing_at: string | null;
  shipped_at: string | null;
  delivered_at: string | null;
  cancelled_at: string | null;
  refunded_at: string | null;
};

export type OrderListItem = {
  id: string;
  customer: number;
  customer_name: string;
  customer_email: string;
  status: OrderStatus;
  payment_status: PaymentStatus;
  shipping_status: ShippingStatus;
  currency: string;
  totals: OrderTotals | null;
  created_at: string;
  updated_at: string;
};

export type OrderDetail = {
  id: string;
  customer: number;
  customer_name: string;
  customer_email: string;
  status: OrderStatus;
  payment_status: PaymentStatus;
  shipping_status: ShippingStatus;
  currency: string;
  items: OrderItem[];
  totals: OrderTotals | null;
  address: OrderAddress | null;
  events: OrderEvent[];
  notes: OrderNote[];
  created_at: string;
  updated_at: string;
};

export type OrderManagementListItem = OrderListItem;

export type OrderManagementDetail = OrderDetail & {
  lifecycle: OrderLifecycle | null;
};