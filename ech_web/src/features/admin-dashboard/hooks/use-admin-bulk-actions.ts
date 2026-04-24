"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { executeBulkOrderAction } from "@/features/admin-dashboard/api/bulk-order-actions";
import { retryBulkNotifications } from "@/features/admin-dashboard/api/bulk-notification-retry";
import { executeBulkReviewModeration } from "@/features/admin-dashboard/api/bulk-review-moderation";
import type {
  BulkNotificationRetryInput,
  BulkOrderActionInput,
  BulkReviewModerationInput,
} from "@/features/admin-dashboard/types/admin-dashboard";
import { adminDashboardQueryKeys } from "@/features/admin-dashboard/utils/admin-dashboard-query-keys";

export function useAdminBulkActions() {
  const queryClient = useQueryClient();

  const invalidateAdminDashboard = () => {
    queryClient.invalidateQueries({
      queryKey: adminDashboardQueryKeys.all,
    });
  };

  const bulkOrderAction = useMutation({
    mutationFn: (payload: BulkOrderActionInput) =>
      executeBulkOrderAction(payload),
    onSuccess: invalidateAdminDashboard,
  });

  const bulkReviewModeration = useMutation({
    mutationFn: (payload: BulkReviewModerationInput) =>
      executeBulkReviewModeration(payload),
    onSuccess: invalidateAdminDashboard,
  });

  const bulkNotificationRetry = useMutation({
    mutationFn: (payload: BulkNotificationRetryInput) =>
      retryBulkNotifications(payload),
    onSuccess: invalidateAdminDashboard,
  });

  return {
    bulkOrderAction,
    bulkReviewModeration,
    bulkNotificationRetry,
    isPending:
      bulkOrderAction.isPending ||
      bulkReviewModeration.isPending ||
      bulkNotificationRetry.isPending,
  };
}