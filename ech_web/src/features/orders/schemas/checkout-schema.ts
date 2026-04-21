import { z } from "zod";

export const checkoutAddressSchema = z.object({
  full_name: z.string().min(2, "Full name is required."),
  address_line: z.string().min(3, "Address line is required."),
  city: z.string().min(2, "City is required."),
  state: z.string().min(2, "State is required."),
  country: z.string().min(2, "Country is required."),
  postal_code: z.string().min(3, "Postal code is required."),
  phone: z.string().optional().or(z.literal("")),
});

export const checkoutSchema = z.object({
  full_name: z.string().min(2, "Full name is required."),
  address_line: z.string().min(3, "Address line is required."),
  city: z.string().min(2, "City is required."),
  state: z.string().min(2, "State is required."),
  country: z.string().min(2, "Country is required."),
  postal_code: z.string().min(3, "Postal code is required."),
  phone: z.string().optional().or(z.literal("")),
});

export type CheckoutSchemaValues = z.infer<typeof checkoutSchema>;