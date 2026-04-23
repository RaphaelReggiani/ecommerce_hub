"use client";

import { useState } from "react";

import type { ReviewFiltersInput } from "@/features/reviews/types/review";

type ReviewFiltersProps = {
  initialFilters?: ReviewFiltersInput;
  onApply: (filters: ReviewFiltersInput) => void;
};

type ReviewOrdering = NonNullable<ReviewFiltersInput["ordering"]>;

export function ReviewFilters({
  initialFilters = {},
  onApply,
}: ReviewFiltersProps) {
  const [ordering, setOrdering] = useState<ReviewOrdering | "">(
    initialFilters.ordering ?? "",
  );
  const [ratingMin, setRatingMin] = useState(
    initialFilters.rating_min?.toString() ?? "",
  );
  const [ratingMax, setRatingMax] = useState(
    initialFilters.rating_max?.toString() ?? "",
  );
  const [verifiedOnly, setVerifiedOnly] = useState(
    Boolean(initialFilters.is_verified_purchase),
  );

  function handleApply() {
    onApply({
      ordering: ordering || undefined,
      rating_min: ratingMin ? Number(ratingMin) : undefined,
      rating_max: ratingMax ? Number(ratingMax) : undefined,
      is_verified_purchase: verifiedOnly || undefined,
    });
  }

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 shadow-xl">
      <div className="grid gap-4 md:grid-cols-4">
        <select
          value={ordering}
          onChange={(event) =>
            setOrdering((event.target.value as ReviewOrdering | "") ?? "")
          }
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
        >
          <option value="">Order by</option>
          <option value="newest">Newest</option>
          <option value="oldest">Oldest</option>
          <option value="rating_high">Highest rating</option>
          <option value="rating_low">Lowest rating</option>
        </select>

        <input
          type="number"
          min={1}
          max={5}
          value={ratingMin}
          onChange={(event) => setRatingMin(event.target.value)}
          placeholder="Min rating"
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
        />

        <input
          type="number"
          min={1}
          max={5}
          value={ratingMax}
          onChange={(event) => setRatingMax(event.target.value)}
          placeholder="Max rating"
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
        />

        <label className="flex items-center gap-3 rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-200">
          <input
            type="checkbox"
            checked={verifiedOnly}
            onChange={(event) => setVerifiedOnly(event.target.checked)}
          />
          Verified only
        </label>
      </div>

      <div className="mt-4 flex justify-end">
        <button
          type="button"
          onClick={handleApply}
          className="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-blue-500"
        >
          Apply filters
        </button>
      </div>
    </div>
  );
}