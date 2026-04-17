"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { confirmPasswordReset } from "@/features/users/api/reset-password";
import {
  resetPasswordSchema,
  type ResetPasswordSchemaValues,
} from "@/features/users/schemas/reset-password-schema";

type ResetPasswordFormProps = {
  token?: string;
};

export function ResetPasswordForm({ token = "" }: ResetPasswordFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordSchemaValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      token,
      new_password: "",
    },
  });

  async function onSubmit(values: ResetPasswordSchemaValues) {
    await confirmPasswordReset(values);
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="w-full max-w-md rounded-2xl border border-slate-800 bg-black p-6 shadow-lg"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-white">Reset password</h2>
        <p className="mt-2 text-sm text-slate-400">
          Enter your new password to complete the reset flow.
        </p>
      </div>

      <input type="hidden" {...register("token")} />

      <div className="mb-6">
        <label className="mb-2 block text-sm font-medium text-slate-300">
          New password
        </label>
        <input
          type="password"
          {...register("new_password")}
          className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        />
        {errors.new_password && (
          <p className="mt-2 text-sm text-red-400">
            {errors.new_password.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-xl bg-blue-600 px-4 py-3 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSubmitting ? "Resetting..." : "Reset password"}
      </button>
    </form>
  );
}