import type {
  ProductReviewSummary,
  ReviewDetail,
  ReviewListItem,
  ReviewManagementDetail,
  ReviewModerationAction,
  ReviewStatus,
} from "@/features/reviews/types/review";

export function getReviewStatusLabel(status: ReviewStatus): string {
  const labels: Record<ReviewStatus, string> = {
    pending: "Pending",
    approved: "Approved",
    rejected: "Rejected",
    hidden: "Hidden",
    cancelled: "Cancelled",
  };

  return labels[status];
}

export function getReviewStatusTone(
  status: ReviewStatus,
): "warning" | "success" | "danger" | "muted" | "info" {
  const tones: Record<ReviewStatus, "warning" | "success" | "danger" | "muted" | "info"> = {
    pending: "warning",
    approved: "success",
    rejected: "danger",
    hidden: "muted",
    cancelled: "muted",
  };

  return tones[status];
}

export function canUpdateReview(review: Pick<ReviewDetail, "status">): boolean {
  return review.status === "pending";
}

export function canCancelReview(review: Pick<ReviewDetail, "status">): boolean {
  return review.status === "pending";
}

export function canModerateReview(
  review: Pick<ReviewManagementDetail, "status">,
  action: ReviewModerationAction,
): boolean {
  if (action === "approve") {
    return review.status === "pending" || review.status === "rejected";
  }

  if (action === "reject") {
    return review.status === "pending" || review.status === "approved";
  }

  if (action === "hide") {
    return review.status === "approved";
  }

  if (action === "restore") {
    return review.status === "hidden";
  }

  return false;
}

export function getAverageRatingLabel(summary: ProductReviewSummary): string {
  if (summary.average_rating === null) {
    return "No rating";
  }

  return summary.average_rating.toFixed(1);
}

export function getTotalRatingDistribution(
  summary: ProductReviewSummary,
  rating: number,
): number {
  const raw = summary.rating_distribution[String(rating)] ?? 0;
  return Number(raw);
}

export function hasVisibleModerationInfo(
  review: Pick<ReviewListItem, "moderation_reason" | "moderated_at">,
): boolean {
  return Boolean(review.moderation_reason || review.moderated_at);
}

export function getReviewErrorMessage(message: string): string {
  const normalized = message.toLowerCase();

  if (normalized.includes("already submitted a review")) {
    return "You already reviewed this product.";
  }

  if (normalized.includes("not allowed to create")) {
    return "You cannot create a review for this product.";
  }

  if (normalized.includes("not allowed to update")) {
    return "You cannot update this review.";
  }

  if (normalized.includes("cannot be cancelled")) {
    return "This review can no longer be cancelled.";
  }

  if (normalized.includes("rating must be between 1 and 5")) {
    return "Rating must be between 1 and 5.";
  }

  if (normalized.includes("not found")) {
    return "Review not found.";
  }

  return message;
}