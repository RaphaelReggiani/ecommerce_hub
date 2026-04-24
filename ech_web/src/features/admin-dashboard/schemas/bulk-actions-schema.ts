import { z } from "zod";

export const bulkOrderActionSchema = z.object({
  action_type: z.string().min(1, "Action type is required."),
  order_ids: z.array(z.string().uuid()).min(1, "At least one order is required."),
});

export const bulkReviewModerationSchema = z.object({
  moderation_action: z.string().min(1, "Moderation action is required."),
  review_ids: z.array(z.string().uuid()).min(1, "At least one review is required."),
  reason: z.string().optional(),
});

export const bulkNotificationRetrySchema = z.object({
  notification_ids: z
    .array(z.string().uuid())
    .min(1, "At least one notification is required."),
});

export type BulkOrderActionValues = z.infer<typeof bulkOrderActionSchema>;
export type BulkReviewModerationValues = z.infer<
  typeof bulkReviewModerationSchema
>;
export type BulkNotificationRetryValues = z.infer<
  typeof bulkNotificationRetrySchema
>;