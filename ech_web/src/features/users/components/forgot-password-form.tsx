"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { requestPasswordReset } from "@/features/users/api/forgot-password";
import {
  forgotPasswordSchema,
  type ForgotPasswordSchemaValues,
} from "@/features/users/schemas/forgot-password-schema";

export function ForgotPasswordForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordSchemaValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: "",
    },
  });

  async function onSubmit(values: ForgotPasswordSchemaValues) {
    await requestPasswordReset(values);
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="w-full max-w-md rounded-2xl border border-slate-800 bg-black p-6 shadow-lg"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-white">Forgot password</h2>
        <p className="mt-2 text-sm text-slate-400">
          Enter your email to request a password reset link.
        </p>
      </div>

      <div className="mb-6">
        <label className="mb-2 block text-sm font-medium text-slate-300">
          Email
        </label>
        <input
          type="email"
          {...register("email")}
          className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        />
        {errors.email && (
          <p className="mt-2 text-sm text-red-400">{errors.email.message}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-xl bg-blue-600 px-4 py-3 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSubmitting ? "Sending..." : "Send reset link"}
      </button>
    </form>
  );
}