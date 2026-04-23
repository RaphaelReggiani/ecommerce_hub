import { z } from "zod";

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

export const createNotificationSchema = z.object({
  recipient_id: z.coerce.number().int().positive("Recipient is required."),
  channel: z.enum(notificationChannelValues),
  notification_type: z
    .string()
    .min(1, "Notification type is required.")
    .max(100, "Notification type is too long."),
  title: z
    .string()
    .min(1, "Title is required.")
    .max(255, "Title is too long."),
  message: z.string().min(1, "Message is required."),
  priority: z.enum(notificationPriorityValues).default("normal"),
  source_module: z.string().max(50, "Source module is too long.").optional(),
  source_event: z.string().max(100, "Source event is too long.").optional(),
  source_object_id: z
    .string()
    .max(64, "Source object id is too long.")
    .optional(),
  scheduled_for: z.string().optional(),
  metadata: z.record(z.string(), z.unknown()).nullable().optional(),
  idempotency_key: z.string().uuid().optional(),
});

export type CreateNotificationSchemaValues = z.infer<
  typeof createNotificationSchema
>;