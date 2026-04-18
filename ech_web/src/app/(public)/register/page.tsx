"use client";

import { RegisterForm } from "@/features/users/components/register-form";

export default function RegisterPage() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-semibold text-white">Create account</h1>
        <p className="mt-2 text-sm text-slate-400">
          Register to start shopping
        </p>
      </div>

      <RegisterForm />
    </div>
  );
}