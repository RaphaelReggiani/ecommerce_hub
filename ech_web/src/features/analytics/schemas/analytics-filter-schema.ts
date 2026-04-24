import { z } from "zod";

export const analyticsFilterSchema = z.object({
  period_type: z.enum(["daily", "weekly", "monthly"]),
  period_start: z.string().optional(),
  period_end: z.string().optional(),
});

export type AnalyticsFilterValues = z.infer<typeof analyticsFilterSchema>;