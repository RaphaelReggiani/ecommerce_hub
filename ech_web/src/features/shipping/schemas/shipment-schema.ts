
import { z } from "zod";

const shippingMethodValues = [
  "standard",
  "express",
  "same_day",
  "pickup_point",
] as const;

const shipmentStatusValues = [
  "pending",
  "preparing",
  "ready_to_ship",
  "shipped",
  "in_transit",
  "out_for_delivery",
  "delivered",
  "failed",
  "returned",
  "cancelled",
] as const;

export const shipmentAddressSchema = z.object({
  full_name: z.string().min(1, "Full name is required"),
  address_line: z.string().min(1, "Address line is required"),
  city: z.string().min(1, "City is required"),
  state: z.string().min(1, "State is required"),
  country: z.string().min(1, "Country is required"),
  postal_code: z.string().min(1, "Postal code is required"),
  phone: z.string().optional(),
  delivery_instructions: z.string().optional(),
});

export const createShipmentSchema = z.object({
  order_id: z.string().uuid("Invalid order id"),
  shipping_method: z.enum(shippingMethodValues),
  address_data: shipmentAddressSchema,
  shipping_cost: z.string().optional(),
  currency: z.string().optional(),
  carrier_name: z.string().optional(),
  tracking_code: z.string().optional(),
  external_reference: z.string().optional(),
  estimated_delivery_date: z.string().optional(),
});

export type CreateShipmentSchemaValues = z.infer<typeof createShipmentSchema>;

export const updateShipmentSchema = z.object({
  shipment_data: z
    .object({
      shipping_method: z.enum(shippingMethodValues).optional(),
      carrier_name: z.string().optional(),
      tracking_code: z.string().nullable().optional(),
      external_reference: z.string().nullable().optional(),
      shipping_cost: z.string().optional(),
      currency: z.string().optional(),
      estimated_delivery_date: z.string().nullable().optional(),
      delivered_to_name: z.string().optional(),
      is_return_to_sender: z.boolean().optional(),
    })
    .optional(),
  address_data: shipmentAddressSchema.partial().optional(),
});

export type UpdateShipmentSchemaValues = z.infer<typeof updateShipmentSchema>;

export const processShipmentSchema = z.object({
  new_status: z.enum(shipmentStatusValues),
});

export type ProcessShipmentSchemaValues = z.infer<typeof processShipmentSchema>;

export const trackShipmentSchema = z.object({
  status: z.enum(shipmentStatusValues).optional(),
  description: z.string().min(1, "Description is required"),
  location: z.string().optional(),
  event_at: z.string().min(1, "Event date is required"),
  tracking_code: z.string().optional(),
  carrier_name: z.string().optional(),
  external_reference: z.string().optional(),
});

export type TrackShipmentSchemaValues = z.infer<typeof trackShipmentSchema>;