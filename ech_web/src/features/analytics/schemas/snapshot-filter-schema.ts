import { z } from "zod";

export const snapshotFilterSchema = z.object({
  period_type: z.string().optional(),
  total_revenue_min: z.number().optional(),
  total_revenue_max: z.number().optional(),
  total_orders_min: z.number().optional(),
  total_orders_max: z.number().optional(),
});

export type SnapshotFilterValues = z.infer<typeof snapshotFilterSchema>;