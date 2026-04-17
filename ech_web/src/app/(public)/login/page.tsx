"use client";

import { LoginForm } from "@/features/users/components/login-form";

export default function LoginPage() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-semibold text-white">Sign in</h1>
        <p className="mt-2 text-sm text-slate-400">
          Access your account to continue
        </p>
      </div>

      <LoginForm />
    </div>
  );
}