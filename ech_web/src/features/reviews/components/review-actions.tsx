"use client";

import { useState } from "react";

import { ConfirmActionDialog } from "@/components/shared/confirm-action-dialog";
import { useCancelReview } from "@/features/reviews/hooks/use-cancel-review";
import { useModerateReview } from "@/features/reviews/hooks/use-moderate-review";
import { useUpdateReview } from "@/features/reviews/hooks/use-update-review";
import type {
  ReviewDetail,
  ReviewManagementDetail,
  ReviewModerationAction,
} from "@/features/reviews/types/review";
import {
  canCancelReview,
  canModerateReview,
  canUpdateReview,
  getReviewErrorMessage,
} from "@/features/reviews/utils/review-mappers";
import { ApiClientError } from "@/lib/api/error-handler";

type ReviewActionsProps = {
  review: ReviewDetail | ReviewManagementDetail;
  mode?: "customer" | "management";
};

export function ReviewActions({
  review,
  mode = "customer",
}: ReviewActionsProps) {
  const updateMutation = useUpdateReview(review.id);
  const cancelMutation = useCancelReview(review.id);
  const moderateMutation = useModerateReview(review.id);

  const [pendingAction, setPendingAction] = useState<ReviewModerationAction | "cancel" | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  async function handleConfirm() {
    if (!pendingAction) return;

    setActionError(null);

    try {
      if (pendingAction === "cancel") {
        await cancelMutation.mutateAsync({});
      } else {
        await moderateMutation.mutateAsync({ action: pendingAction });
      }

      setPendingAction(null);
    } catch (error) {
      if (error instanceof ApiClientError) {
        setActionError(getReviewErrorMessage(error.message));
        return;
      }

      setActionError("Unable to complete this review action right now.");
    }
  }

  const isPending =
    updateMutation.isPending ||
    cancelMutation.isPending ||
    moderateMutation.isPending;

  const isManagement = mode === "management";
  const customerCanEdit = mode === "customer" && canUpdateReview(review);
  const customerCanCancel = mode === "customer" && canCancelReview(review);

  return (
    <>
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
        <div className="mb-4">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Actions
          </p>
          <h3 className="mt-2 text-xl font-semibold text-white">
            Review operations
          </h3>
        </div>

        {actionError ? (
          <div className="mb-4 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {actionError}
          </div>
        ) : null}

        <div className="flex flex-wrap gap-3">
          {customerCanEdit ? (
            <button
              type="button"
              onClick={() =>
                updateMutation.mutate({
                  rating: review.rating,
                  title: review.title,
                  comment: review.comment,
                })
              }
              className="rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
            >
              Save current values
            </button>
          ) : null}

          {customerCanCancel ? (
            <button
              type="button"
              onClick={() => setPendingAction("cancel")}
              className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-300 transition hover:bg-red-500/20"
            >
              Cancel review
            </button>
          ) : null}

          {isManagement && canModerateReview(review as ReviewManagementDetail, "approve") ? (
            <button
              type="button"
              onClick={() => setPendingAction("approve")}
              className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-300 transition hover:bg-emerald-500/20"
            >
              Approve
            </button>
          ) : null}

          {isManagement && canModerateReview(review as ReviewManagementDetail, "reject") ? (
            <button
              type="button"
              onClick={() => setPendingAction("reject")}
              className="rounded-2xl border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm font-medium text-amber-300 transition hover:bg-amber-500/20"
            >
              Reject
            </button>
          ) : null}

          {isManagement && canModerateReview(review as ReviewManagementDetail, "hide") ? (
            <button
              type="button"
              onClick={() => setPendingAction("hide")}
              className="rounded-2xl border border-slate-600 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-slate-400 hover:text-white"
            >
              Hide
            </button>
          ) : null}

          {isManagement && canModerateReview(review as ReviewManagementDetail, "restore") ? (
            <button
              type="button"
              onClick={() => setPendingAction("restore")}
              className="rounded-2xl border border-blue-500/30 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-300 transition hover:bg-blue-500/20"
            >
              Restore
            </button>
          ) : null}
        </div>
      </div>

      <ConfirmActionDialog
        isOpen={Boolean(pendingAction)}
        title="Confirm review action"
        description="This action will change the current review state. Confirm to continue."
        confirmLabel="Confirm"
        cancelLabel="Back"
        isPending={isPending}
        tone={pendingAction === "cancel" ? "danger" : "default"}
        onConfirm={handleConfirm}
        onCancel={() => setPendingAction(null)}
      />
    </>
  );
}