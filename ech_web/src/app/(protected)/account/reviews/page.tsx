"use client";

import Link from "next/link";
import { useState } from "react";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { useReviews } from "@/features/reviews/hooks/use-reviews";
import { ReviewFilters } from "@/features/reviews/components/review-filters";
import { ReviewStatusBadge } from "@/features/reviews/components/review-status-badge";
import type { ReviewFiltersInput } from "@/features/reviews/types/review";
import { formatDateTime } from "@/lib/utils/format-date";

export default function AccountReviewsPage() {
  const [filters, setFilters] = useState<ReviewFiltersInput>({});
  const { data, isLoading, isError, refetch } = useReviews(filters);

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState
          title="Loading reviews..."
          description="Please wait while we load your reviews."
        />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load reviews."
          description="We could not retrieve your reviews right now."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Reviews"
        title="Your reviews"
        description="Review your product feedback, moderation status, and review history."
      />

      <ReviewFilters onApply={setFilters} initialFilters={filters} />

      {!data.results.length ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-10 text-center text-slate-400 shadow-xl">
          No reviews found.
        </div>
      ) : (
        <div className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/70 shadow-xl">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-800">
              <thead className="bg-slate-950/70">
                <tr>
                  <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                    Product
                  </th>
                  <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                    Rating
                  </th>
                  <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                    Verified
                  </th>
                  <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                    Created
                  </th>
                  <th className="px-6 py-4 text-right text-xs uppercase tracking-[0.2em] text-slate-500">
                    Action
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-800">
                {data.results.map((review) => (
                  <tr key={review.id} className="hover:bg-slate-950/40">
                    <td className="px-6 py-4 text-sm text-white">
                      <div className="font-medium">{review.product.name}</div>
                      <div className="text-slate-500">{review.product.brand}</div>
                    </td>

                    <td className="px-6 py-4 text-sm text-slate-300">
                      {review.rating}/5
                    </td>

                    <td className="px-6 py-4">
                      <ReviewStatusBadge status={review.status} />
                    </td>

                    <td className="px-6 py-4 text-sm text-slate-300">
                      {review.is_verified_purchase ? "Yes" : "No"}
                    </td>

                    <td className="px-6 py-4 text-sm text-slate-400">
                      {formatDateTime(review.created_at)}
                    </td>

                    <td className="px-6 py-4 text-right">
                      <Link
                        href={`/account/reviews/${review.id}`}
                        className="inline-flex rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white"
                      >
                        View details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </PageContainer>
  );
}