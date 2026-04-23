import { ReviewStatusBadge } from "@/features/reviews/components/review-status-badge";
import { RatingStars } from "@/features/reviews/components/rating-stars";
import type {
  ProductPublicReview,
  ReviewListItem,
} from "@/features/reviews/types/review";
import { formatDateTime } from "@/lib/utils/format-date";

type ReviewCardProps = {
  review: ReviewListItem | ProductPublicReview;
  showStatus?: boolean;
};

export function ReviewCard({
  review,
  showStatus = false,
}: ReviewCardProps) {
  const hasStatus = showStatus && "status" in review;

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-2">
          {"customer" in review ? (
            <p className="text-sm font-medium text-slate-200">
              {review.customer.user_name}
            </p>
          ) : null}

          <RatingStars rating={review.rating} />

          {review.title ? (
            <h3 className="text-lg font-semibold text-white">{review.title}</h3>
          ) : null}

          {review.comment ? (
            <p className="text-sm leading-7 text-slate-300">{review.comment}</p>
          ) : (
            <p className="text-sm text-slate-500">No comment provided.</p>
          )}
        </div>

        <div className="space-y-2 text-left sm:text-right">
          {hasStatus ? (
            <ReviewStatusBadge status={review.status} />
          ) : null}

          {"is_verified_purchase" in review && review.is_verified_purchase ? (
            <p className="text-xs uppercase tracking-[0.18em] text-emerald-400">
              Verified purchase
            </p>
          ) : null}

          <p className="text-xs text-slate-500">
            {formatDateTime(review.created_at)}
          </p>
        </div>
      </div>
    </div>
  );
}