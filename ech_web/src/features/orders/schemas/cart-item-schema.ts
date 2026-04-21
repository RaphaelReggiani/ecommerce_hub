import { z } from "zod";

export const cartItemSchema = z.object({
  product_id: z.string().uuid(),
  name: z.string().min(1),
  brand: z.string().min(1),
  product_type: z.string().min(1),
  main_image: z.string().nullable(),
  unit_price: z.string(),
  discount_price: z.string().nullable(),
  quantity: z.number().int().positive(),
  max_quantity: z.number().int().positive().optional(),
});

export type CartItemSchemaValues = z.infer<typeof cartItemSchema>;