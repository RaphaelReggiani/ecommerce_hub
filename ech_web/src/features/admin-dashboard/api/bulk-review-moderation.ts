import { apiClient } from "@/lib/api/client";
import type {
  BulkReviewModerationInput,
  BulkReviewModerationResponse,
} from "@/features/admin-dashboard/types/admin-dashboard";

export async function executeBulkReviewModeration(
  payload: BulkReviewModerationInput,
): Promise<BulkReviewModerationResponse> {
  return apiClient.post<BulkReviewModerationResponse>(
    "/admin-dashboard/reviews/bulk-moderation/",
    payload,
    { auth: true },
  );
}