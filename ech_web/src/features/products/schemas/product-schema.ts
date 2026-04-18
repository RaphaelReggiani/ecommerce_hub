import { z } from "zod";

export const productSchema = z
  .object({
    name: z
      .string()
      .min(1, "Product name is required.")
      .max(255, "Name must contain at most 255 characters."),
    product_type: z.enum([
      "PHONE",
      "EARPHONE",
      "HEADSET",
      "MOUSE",
      "KEYBOARD",
      "MICROPHONE",
    ]),
    brand: z
      .string()
      .min(1, "Brand is required.")
      .max(120, "Brand must contain at most 120 characters."),
    description: z.string().min(1, "Description is required."),
    technical_information: z.string().min(1, "Technical information is required."),
    price: z.number().positive("Price must be greater than zero."),
    discount_price: z
      .number()
      .positive("Discount price must be greater than zero.")
      .nullable()
      .optional(),
    inventory: z.number().min(0, "Inventory cannot be negative."),
  })
  .refine(
    (data) =>
      data.discount_price === null ||
      data.discount_price === undefined ||
      data.discount_price < data.price,
    {
      message: "Discount price must be lower than price.",
      path: ["discount_price"],
    },
  );

export type ProductSchemaValues = z.infer<typeof productSchema>;