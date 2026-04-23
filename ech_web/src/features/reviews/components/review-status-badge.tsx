import { StatusBadge } from "@/components/shared/status-badge";

import type { ReviewStatus } from "@/features/reviews/types/review";
import {
  getReviewStatusLabel,
  getReviewStatusTone,
} from "@/features/reviews/utils/review-mappers";

type ReviewStatusBadgeProps = {
  status: ReviewStatus;
};

export function ReviewStatusBadge({ status }: ReviewStatusBadgeProps) {
  return (
    <StatusBadge tone={getReviewStatusTone(status)}>
      {getReviewStatusLabel(status)}
    </StatusBadge>
  );
}