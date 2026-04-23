import { z } from "zod";

const notificationStatusValues = [
  "pending",
  "unread",
  "read",
  "archived",
  "cancelled",
  "failed",
] as const;

const notificationChannelValues = [
  "in_app",
  "email",
  "both",
] as const;

const notificationPriorityValues = [
  "low",
  "normal",
  "high",
  "critical",
] as const;

export const notificationFilterSchema = z.object({
  status: z.enum(notificationStatusValues).optional(),
  channel: z.enum(notificationChannelValues).optional(),
  priority: z.enum(notificationPriorityValues).optional(),
  notification_type: z.string().optional(),
  source_module: z.string().optional(),
  created_after: z.string().optional(),
  created_before: z.string().optional(),
  scheduled_after: z.string().optional(),
  scheduled_before: z.string().optional(),
  page: z.coerce.number().int().positive().optional(),
});

export type NotificationFilterSchemaValues = z.infer<
  typeof notificationFilterSchema
>;