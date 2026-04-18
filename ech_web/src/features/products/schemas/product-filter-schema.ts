import { z } from "zod";

export const productFilterSchema = z.object({
  search: z.string().optional(),
  ordering: z.string().optional(),
  product_type: z.string().optional(),
  brand: z.string().optional(),
  page: z.coerce.number().optional(),
  pageSize: z.coerce.number().optional(),
});

export type ProductFilterSchemaValues = z.infer<typeof productFilterSchema>;