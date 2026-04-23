"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm, type SubmitHandler } from "react-hook-form";

import { useCreateReview } from "@/features/reviews/hooks/use-create-review";
import {
  createReviewSchema,
  type CreateReviewSchemaValues,
} from "@/features/reviews/schemas/review-schema";
import { getReviewErrorMessage } from "@/features/reviews/utils/review-mappers";
import { ApiClientError } from "@/lib/api/error-handler";

type ReviewFormProps = {
  productId: string;
  onSuccess?: () => void;
};

export function ReviewForm({ productId, onSuccess }: ReviewFormProps) {
  const createReviewMutation = useCreateReview();
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateReviewSchemaValues>({
    resolver: zodResolver(createReviewSchema),
    defaultValues: {
      product_id: productId,
      rating: 5,
      title: "",
      comment: "",
      is_verified_purchase: false,
    },
  });

  const onSubmit: SubmitHandler<CreateReviewSchemaValues> = async (values) => {
    setFormError(null);

    try {
      await createReviewMutation.mutateAsync(values);
      onSuccess?.();
    } catch (error) {
      if (error instanceof ApiClientError) {
        setFormError(getReviewErrorMessage(error.message));
        return;
      }

      setFormError("Unable to create review right now.");
    }
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl"
    >
      <div className="mb-6">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
          Review
        </p>
        <h2 className="mt-2 text-2xl font-semibold text-white">
          Write a review
        </h2>
      </div>

      {formError ? (
        <div className="mb-4 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {formError}
        </div>
      ) : null}

      <input type="hidden" {...register("product_id")} />

      <div className="mb-4">
        <label className="mb-2 block text-sm font-medium text-slate-300">
          Rating
        </label>
        <select
          {...register("rating", { valueAsNumber: true })}
          className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        >
          <option value={5}>5</option>
          <option value={4}>4</option>
          <option value={3}>3</option>
          <option value={2}>2</option>
          <option value={1}>1</option>
        </select>
        {errors.rating ? (
          <p className="mt-2 text-sm text-red-400">{errors.rating.message}</p>
        ) : null}
      </div>

      <div className="mb-4">
        <label className="mb-2 block text-sm font-medium text-slate-300">
          Title
        </label>
        <input
          type="text"
          {...register("title")}
          className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        />
      </div>

      <div className="mb-4">
        <label className="mb-2 block text-sm font-medium text-slate-300">
          Comment
        </label>
        <textarea
          {...register("comment")}
          rows={5}
          className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        />
      </div>

      <label className="mb-6 flex items-center gap-3 text-sm text-slate-300">
        <input type="checkbox" {...register("is_verified_purchase")} />
        Mark as verified purchase
      </label>

      <button
        type="submit"
        disabled={createReviewMutation.isPending}
        className="w-full rounded-2xl bg-blue-600 px-4 py-3 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {createReviewMutation.isPending ? "Submitting review..." : "Submit review"}
      </button>
    </form>
  );
}