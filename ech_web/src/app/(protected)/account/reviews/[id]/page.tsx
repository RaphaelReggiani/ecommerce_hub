"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { ReviewActions } from "@/features/reviews/components/review-actions";
import { ReviewStatusBadge } from "@/features/reviews/components/review-status-badge";
import { RatingStars } from "@/features/reviews/components/rating-stars";
import { useReview } from "@/features/reviews/hooks/use-review";
import { formatDateTime } from "@/lib/utils/format-date";

export default function AccountReviewDetailPage() {
  const params = useParams<{ id: string }>();
  const reviewId = params?.id;
  const { data, isLoading, isError, refetch } = useReview(reviewId);

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState
          title="Loading review..."
          description="Please wait while we load the review details."
        />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load review."
          description="We could not retrieve this review right now."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Review detail"
        title={data.title || "Review"}
        description="Review your feedback details, moderation info, and lifecycle."
        actions={
          <Link
            href="/account/reviews"
            className="inline-flex items-center rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
          >
            Back to reviews
          </Link>
        }
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
        <div className="mb-6 flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Product
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              {data.product.name}
            </h2>
            <p className="mt-2 text-sm text-slate-400">
              {data.product.brand} • {data.product.product_type}
            </p>
          </div>

          <ReviewStatusBadge status={data.status} />
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
              Rating
            </p>
            <div className="mt-2">
              <RatingStars rating={data.rating} />
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
              Verified purchase
            </p>
            <p className="mt-2 text-sm text-white">
              {data.is_verified_purchase ? "Yes" : "No"}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
              Created
            </p>
            <p className="mt-2 text-sm text-white">
              {formatDateTime(data.created_at)}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4 md:col-span-2 xl:col-span-3">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
              Title
            </p>
            <p className="mt-2 text-sm text-white">{data.title || "-"}</p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4 md:col-span-2 xl:col-span-3">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
              Comment
            </p>
            <p className="mt-2 text-sm leading-7 text-slate-300">
              {data.comment || "No comment provided."}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4 md:col-span-2 xl:col-span-3">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
              Moderation
            </p>
            <p className="mt-2 text-sm text-white">
              Reason: {data.moderation_reason || "-"}
            </p>
            <p className="mt-1 text-xs text-slate-400">
              Moderated at: {data.moderated_at ? formatDateTime(data.moderated_at) : "-"}
            </p>
          </div>
        </div>
      </div>

      {data.lifecycle ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Lifecycle
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              Review lifecycle
            </h2>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {[
              ["Approved", data.lifecycle.approved_at],
              ["Rejected", data.lifecycle.rejected_at],
              ["Hidden", data.lifecycle.hidden_at],
              ["Cancelled", data.lifecycle.cancelled_at],
            ].map(([label, value]) => (
              <div
                key={label}
                className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
              >
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                  {label}
                </p>
                <p className="mt-2 text-sm text-slate-200">
                  {typeof value === "string" && value
                    ? formatDateTime(value)
                    : "Not reached"}
                </p>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      <ReviewActions review={data} mode="customer" />
    </PageContainer>
  );
}