"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { useLogin } from "@/features/users/hooks/use-login";
import { loginSchema, type LoginSchemaValues } from "@/features/users/schemas/login-schema";

export function LoginForm() {
  const loginMutation = useLogin();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginSchemaValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  async function onSubmit(values: LoginSchemaValues) {
    await loginMutation.mutateAsync(values);
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="w-full max-w-md rounded-2xl border border-slate-800 bg-black p-6 shadow-lg"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-white">Sign in</h2>
        <p className="mt-2 text-sm text-slate-400">
          Access your E-commerce Hub account.
        </p>
      </div>

      <div className="mb-4">
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

      <div className="mb-6">
        <label className="mb-2 block text-sm font-medium text-slate-300">
          Password
        </label>
        <input
          type="password"
          {...register("password")}
          className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        />
        {errors.password && (
          <p className="mt-2 text-sm text-red-400">{errors.password.message}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={loginMutation.isPending}
        className="w-full rounded-xl bg-blue-600 px-4 py-3 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loginMutation.isPending ? "Signing in..." : "Sign in"}
      </button>
    </form>
  );
}