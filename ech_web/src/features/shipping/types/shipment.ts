export type ShipmentStatus =
  | "pending"
  | "preparing"
  | "ready_to_ship"
  | "shipped"
  | "in_transit"
  | "out_for_delivery"
  | "delivered"
  | "failed"
  | "returned"
  | "cancelled";

export type ShippingMethod =
  | "standard"
  | "express"
  | "same_day"
  | "pickup_point";

export type ShipmentEventType =
  | "shipment_created"
  | "shipment_updated"
  | "shipment_status_changed"
  | "shipment_preparing_started"
  | "shipment_ready_to_ship"
  | "shipment_shipped"
  | "shipment_in_transit"
  | "shipment_out_for_delivery"
  | "shipment_delivered"
  | "shipment_failed"
  | "shipment_returned"
  | "shipment_cancelled"
  | "shipment_tracking_updated";

export type ShipmentAddress = {
  full_name: string;
  address_line: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  phone: string;
  delivery_instructions: string;
  created_at: string;
  updated_at: string;
};

export type ShipmentLifecycle = {
  preparing_at: string | null;
  ready_to_ship_at: string | null;
  shipped_at: string | null;
  in_transit_at: string | null;
  out_for_delivery_at: string | null;
  delivered_at: string | null;
  failed_at: string | null;
  returned_at: string | null;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ShipmentEvent = {
  id: string;
  event_type: ShipmentEventType | string;
  performed_by: number | null;
  performed_by_name: string | null;
  performed_by_email: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export type ShipmentTrackingUpdate = {
  id: string;
  status: ShipmentStatus | "";
  description: string;
  location: string;
  raw_payload: Record<string, unknown> | null;
  event_at: string;
  created_at: string;
};

export type ShipmentNote = {
  id: string;
  author: number | null;
  author_name: string | null;
  author_email: string | null;
  message: string;
  is_internal: boolean;
  created_at: string;
};

export type ShipmentListItem = {
  id: string;
  order: string;
  customer: number;
  customer_name: string;
  customer_email: string;
  status: ShipmentStatus;
  shipping_method: ShippingMethod;
  carrier_name: string;
  tracking_code: string | null;
  external_reference: string | null;
  shipping_cost: string;
  currency: string;
  estimated_delivery_date: string | null;
  created_at: string;
  updated_at: string;
};

export type ShipmentDetail = ShipmentListItem & {
  delivered_to_name: string;
  is_return_to_sender: boolean;
  address: ShipmentAddress | null;
  lifecycle: ShipmentLifecycle | null;
  events: ShipmentEvent[];
  tracking_updates: ShipmentTrackingUpdate[];
  visible_notes: ShipmentNote[];
};

export type ShipmentManagementDetail = ShipmentListItem & {
  delivered_to_name: string;
  is_return_to_sender: boolean;
  address: ShipmentAddress | null;
  lifecycle: ShipmentLifecycle | null;
  events: ShipmentEvent[];
  tracking_updates: ShipmentTrackingUpdate[];
  notes: ShipmentNote[];
};

export type ShipmentFiltersInput = {
  status?: ShipmentStatus;
  shipping_method?: ShippingMethod;
  carrier_name?: string;
  tracking_code?: string;
  created_after?: string;
  created_before?: string;
  estimated_delivery_after?: string;
  estimated_delivery_before?: string;
  page?: number;
};

export type ShipmentAddressInput = {
  full_name: string;
  address_line: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  phone?: string;
  delivery_instructions?: string;
};

export type CreateShipmentInput = {
  order_id: string;
  shipping_method: ShippingMethod;
  address_data: ShipmentAddressInput;
  shipping_cost?: string;
  currency?: string;
  carrier_name?: string;
  tracking_code?: string | null;
  external_reference?: string | null;
  estimated_delivery_date?: string | null;
  idempotency_key?: string;
};

export type ShipmentUpdateDataInput = Partial<{
  shipping_method: ShippingMethod;
  carrier_name: string;
  tracking_code: string | null;
  external_reference: string | null;
  shipping_cost: string;
  currency: string;
  estimated_delivery_date: string | null;
  delivered_to_name: string;
  is_return_to_sender: boolean;
}>;

export type UpdateShipmentInput = {
  shipment_data?: ShipmentUpdateDataInput;
  address_data?: ShipmentAddressInput;
};

export type ProcessShipmentInput = {
  new_status: ShipmentStatus;
  metadata?: Record<string, unknown>;
};

export type CancelShipmentInput = {
  metadata?: Record<string, unknown>;
};

export type TrackShipmentInput = {
  status?: ShipmentStatus;
  description: string;
  location?: string;
  raw_payload?: Record<string, unknown>;
  event_at: string;
  tracking_code?: string;
  carrier_name?: string;
  external_reference?: string;
};