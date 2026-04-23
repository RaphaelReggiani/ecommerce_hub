import { EmptyState } from "@/components/feedback/empty-state";

import { ReviewCard } from "@/features/reviews/components/review-card";
import type {
  ProductPublicReview,
  ReviewListItem,
} from "@/features/reviews/types/review";

type ReviewListProps = {
  reviews: ReviewListItem[] | ProductPublicReview[];
  showStatus?: boolean;
};

export function ReviewList({
  reviews,
  showStatus = false,
}: ReviewListProps) {
  if (!reviews.length) {
    return (
      <EmptyState
        title="No reviews found."
        description="There are no reviews available for this view."
      />
    );
  }

  return (
    <div className="space-y-4">
      {reviews.map((review) => (
        <ReviewCard
          key={review.id}
          review={review}
          showStatus={showStatus}
        />
      ))}
    </div>
  );
}