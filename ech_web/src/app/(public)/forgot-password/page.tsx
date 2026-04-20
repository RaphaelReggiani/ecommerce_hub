"use client";

import { ForgotPasswordForm } from "@/features/users/components/forgot-password-form";

export default function ForgotPasswordPage() {
  return (
    <div className="mx-auto w-full max-w-md rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">
      <div className="mb-6 text-center">
        <h1 className="text-3xl font-semibold text-white">Forgot password</h1>
        <p className="mt-2 text-sm text-slate-400">
          Enter your email to receive reset instructions
        </p>
      </div>

      <ForgotPasswordForm />
    </div>
  );
}