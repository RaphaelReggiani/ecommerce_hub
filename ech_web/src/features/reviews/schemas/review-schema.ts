import { z } from "zod";

const reviewModerationActionValues = [
  "approve",
  "reject",
  "hide",
  "restore",
] as const;

const reviewOrderingValues = [
  "newest",
  "oldest",
  "rating_high",
  "rating_low",
] as const;

export const createReviewSchema = z.object({
  product_id: z.string().uuid("Invalid product id"),
  rating: z
    .number({
      error: "Rating is required",
    })
    .int("Rating must be an integer")
    .min(1, "Rating must be between 1 and 5")
    .max(5, "Rating must be between 1 and 5"),
  title: z.string().max(255, "Title is too long").optional(),
  comment: z.string().optional(),
  is_verified_purchase: z.boolean().optional(),
});

export type CreateReviewSchemaValues = z.infer<typeof createReviewSchema>;

export const updateReviewSchema = z
  .object({
    rating: z
      .number({
        error: "Rating is required",
      })
      .int("Rating must be an integer")
      .min(1, "Rating must be between 1 and 5")
      .max(5, "Rating must be between 1 and 5")
      .optional(),
    title: z.string().max(255, "Title is too long").optional(),
    comment: z.string().optional(),
  })
  .refine(
    (values) =>
      values.rating !== undefined ||
      values.title !== undefined ||
      values.comment !== undefined,
    {
      message: "At least one field must be provided for update.",
    },
  );

export type UpdateReviewSchemaValues = z.infer<typeof updateReviewSchema>;

export const cancelReviewSchema = z.object({
  reason: z.string().optional(),
});

export type CancelReviewSchemaValues = z.infer<typeof cancelReviewSchema>;

export const moderateReviewSchema = z.object({
  action: z.enum(reviewModerationActionValues),
  reason: z.string().optional(),
});

export type ModerateReviewSchemaValues = z.infer<typeof moderateReviewSchema>;

export const reviewFiltersSchema = z.object({
  status: z.string().optional(),
  rating: z.number().optional(),
  rating_min: z.number().optional(),
  rating_max: z.number().optional(),
  is_verified_purchase: z.boolean().optional(),
  ordering: z.enum(reviewOrderingValues).optional(),
});

export type ReviewFiltersSchemaValues = z.infer<typeof reviewFiltersSchema>;