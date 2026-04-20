"use client";

import { useSearchParams } from "next/navigation";

import { LoginForm } from "@/features/users/components/login-form";

export default function LoginPage() {
  const searchParams = useSearchParams();
  const registered = searchParams.get("registered");

  return (
    <div className="mx-auto w-full max-w-md rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">
      <div className="mb-6 text-center">
        <h1 className="text-3xl font-semibold text-white">Sign in</h1>
        <p className="mt-2 text-sm text-slate-400">
          Access your account to continue
        </p>
      </div>

      {registered === "1" && (
        <div className="mb-6 rounded-2xl border border-blue-500/30 bg-blue-500/10 px-4 py-3 text-sm text-blue-300">
          Account created successfully. Please confirm your email before signing in.
        </div>
      )}

      <LoginForm />
    </div>
  );
}