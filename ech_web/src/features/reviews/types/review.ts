export type ReviewStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "hidden"
  | "cancelled";

export type ReviewModerationAction =
  | "approve"
  | "reject"
  | "hide"
  | "restore";

export type ReviewCustomer = {
  id: number;
  user_name: string;
  user_email: string;
};

export type ReviewPublicCustomer = {
  id: number;
  user_name: string;
};

export type ReviewProduct = {
  id: string;
  name: string;
  brand: string;
  product_type: string;
  main_image: string | null;
};

export type ReviewLifecycle = {
  approved_at: string | null;
  rejected_at: string | null;
  hidden_at: string | null;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ReviewEvent = {
  id: string;
  event_type: string;
  performed_by: number | null;
  performed_by_name: string | null;
  performed_by_email: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export type ReviewListItem = {
  id: string;
  product: ReviewProduct;
  rating: number;
  title: string;
  comment: string;
  status: ReviewStatus;
  is_verified_purchase: boolean;
  moderation_reason: string;
  moderated_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ReviewDetail = {
  id: string;
  customer: ReviewCustomer;
  product: ReviewProduct;
  rating: number;
  title: string;
  comment: string;
  status: ReviewStatus;
  is_verified_purchase: boolean;
  moderated_by: number | null;
  moderation_reason: string;
  moderated_at: string | null;
  lifecycle: ReviewLifecycle | null;
  created_at: string;
  updated_at: string;
};

export type ReviewManagementListItem = {
  id: string;
  customer: ReviewCustomer;
  product: ReviewProduct;
  rating: number;
  title: string;
  status: ReviewStatus;
  is_verified_purchase: boolean;
  moderated_by: number | null;
  moderated_by_name: string | null;
  moderated_by_email: string | null;
  moderated_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ReviewManagementDetail = {
  id: string;
  customer: ReviewCustomer;
  product: ReviewProduct;
  rating: number;
  title: string;
  comment: string;
  status: ReviewStatus;
  idempotency_key: string | null;
  is_verified_purchase: boolean;
  moderated_by: number | null;
  moderated_by_name: string | null;
  moderated_by_email: string | null;
  moderation_reason: string;
  moderated_at: string | null;
  lifecycle: ReviewLifecycle | null;
  events: ReviewEvent[];
  created_at: string;
  updated_at: string;
};

export type ProductPublicReview = {
  id: string;
  customer: ReviewPublicCustomer;
  rating: number;
  title: string;
  comment: string;
  is_verified_purchase: boolean;
  created_at: string;
};

export type ProductReviewSummary = {
  product_id: string;
  average_rating: number | null;
  total_reviews: number;
  rating_distribution: Record<string, number>;
  verified_reviews: number;
};

export type ReviewFiltersInput = {
  status?: ReviewStatus;
  rating?: number;
  rating_min?: number;
  rating_max?: number;
  product_id?: string;
  customer_id?: number;
  is_verified_purchase?: boolean;
  moderated_by_id?: number;
  created_after?: string;
  created_before?: string;
  ordering?: "newest" | "oldest" | "rating_high" | "rating_low";
  page?: number;
};

export type CreateReviewInput = {
  product_id: string;
  rating: number;
  title?: string;
  comment?: string;
  idempotency_key?: string;
  is_verified_purchase?: boolean;
};

export type UpdateReviewInput = Partial<{
  rating: number;
  title: string;
  comment: string;
}>;

export type CancelReviewInput = {
  reason?: string;
};

export type ModerateReviewInput = {
  action: ReviewModerationAction;
  reason?: string;
};