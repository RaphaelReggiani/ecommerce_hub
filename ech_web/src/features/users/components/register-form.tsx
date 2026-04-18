"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { ApiClientError } from "@/lib/api/error-handler";
import { useRegister } from "@/features/users/hooks/use-register";
import {
  registerSchema,
  type RegisterSchemaValues,
} from "@/features/users/schemas/register-schema";

export function RegisterForm() {
  const registerMutation = useRegister();
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterSchemaValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: "",
      password: "",
      user_name: "",
    },
  });

  async function onSubmit(values: RegisterSchemaValues) {
    setFormError(null);

    try {
      await registerMutation.mutateAsync(values);
    } catch (error) {
      if (error instanceof ApiClientError) {
        setFormError(error.message);
        return;
      }

      setFormError("Unable to create the account right now.");
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="w-full max-w-md rounded-2xl border border-slate-800 bg-black p-6 shadow-lg"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-white">Create account</h2>
        <p className="mt-2 text-sm text-slate-400">
          Register to access the platform.
        </p>
      </div>

      {formError && (
        <div className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {formError}
        </div>
      )}

      <div className="mb-4">
        <label className="mb-2 block text-sm font-medium text-slate-300">
          Name
        </label>
        <input
          type="text"
          {...register("user_name")}
          className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        />
        {errors.user_name && (
          <p className="mt-2 text-sm text-red-400">{errors.user_name.message}</p>
        )}
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
        disabled={registerMutation.isPending}
        className="w-full rounded-xl bg-blue-600 px-4 py-3 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {registerMutation.isPending ? "Creating account..." : "Create account"}
      </button>
    </form>
  );
}