import { RatingStars } from "@/features/reviews/components/rating-stars";
import type { ProductReviewSummary } from "@/features/reviews/types/review";
import {
  getAverageRatingLabel,
  getTotalRatingDistribution,
} from "@/features/reviews/utils/review-mappers";

type ReviewSummaryProps = {
  summary: ProductReviewSummary;
};

export function ReviewSummary({ summary }: ReviewSummaryProps) {
  const averageValue = summary.average_rating ?? 0;

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <div className="grid gap-6 lg:grid-cols-[0.4fr_0.6fr]">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Review summary
          </p>
          <div className="mt-4 flex items-end gap-3">
            <span className="text-4xl font-semibold text-white">
              {getAverageRatingLabel(summary)}
            </span>
            <span className="pb-1 text-sm text-slate-400">
              / 5
            </span>
          </div>

          <div className="mt-3">
            <RatingStars rating={Math.round(averageValue)} />
          </div>

          <p className="mt-3 text-sm text-slate-400">
            {summary.total_reviews} reviews • {summary.verified_reviews} verified
          </p>
        </div>

        <div className="space-y-3">
          {[5, 4, 3, 2, 1].map((rating) => {
            const count = getTotalRatingDistribution(summary, rating);
            const percentage =
              summary.total_reviews > 0
                ? (count / summary.total_reviews) * 100
                : 0;

            return (
              <div key={rating} className="flex items-center gap-3">
                <span className="w-10 text-sm text-slate-300">
                  {rating}★
                </span>
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-800">
                  <div
                    className="h-full rounded-full bg-blue-500"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <span className="w-10 text-right text-sm text-slate-400">
                  {count}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}