"use client";

import { ResetPasswordForm } from "@/features/users/components/reset-password-form";

export default function ResetPasswordPage() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-semibold text-white">Reset password</h1>
        <p className="mt-2 text-sm text-slate-400">
          Choose a new password for your account
        </p>
      </div>

      <ResetPasswordForm />
    </div>
  );
}