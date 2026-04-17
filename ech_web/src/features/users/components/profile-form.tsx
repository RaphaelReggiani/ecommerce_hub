"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import type { UserProfile } from "@/types/common";
import {
  profileSchema,
  type ProfileSchemaValues,
} from "@/features/users/schemas/profile-schema";

type ProfileFormProps = {
  initialValues: UserProfile;
  onSubmit: (values: ProfileSchemaValues) => Promise<void> | void;
};

export function ProfileForm({ initialValues, onSubmit }: ProfileFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ProfileSchemaValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      user_name: initialValues.user_name,
      user_phone: initialValues.user_phone || "",
      user_country: initialValues.user_country || "",
      user_state: initialValues.user_state || "",
      user_address: initialValues.user_address || "",
      user_age: initialValues.user_age,
    },
  });

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="w-full rounded-2xl border border-slate-800 bg-black p-6 shadow-lg"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-white">Profile</h2>
        <p className="mt-2 text-sm text-slate-400">
          Update your account information.
        </p>
      </div>

      <div className="mb-4 grid gap-4 md:grid-cols-2">
        <div>
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

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Phone
          </label>
          <input
            type="text"
            {...register("user_phone")}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />
          {errors.user_phone && (
            <p className="mt-2 text-sm text-red-400">{errors.user_phone.message}</p>
          )}
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Country
          </label>
          <input
            type="text"
            {...register("user_country")}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />
          {errors.user_country && (
            <p className="mt-2 text-sm text-red-400">{errors.user_country.message}</p>
          )}
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">
            State
          </label>
          <input
            type="text"
            {...register("user_state")}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />
          {errors.user_state && (
            <p className="mt-2 text-sm text-red-400">{errors.user_state.message}</p>
          )}
        </div>

        <div className="md:col-span-2">
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Address
          </label>
          <input
            type="text"
            {...register("user_address")}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />
          {errors.user_address && (
            <p className="mt-2 text-sm text-red-400">{errors.user_address.message}</p>
          )}
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Age
          </label>
          <input
            type="number"
            {...register("user_age", {
              setValueAs: (value) => (value === "" ? null : Number(value)),
            })}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />
          {errors.user_age && (
            <p className="mt-2 text-sm text-red-400">{errors.user_age.message}</p>
          )}
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="mt-6 rounded-xl bg-blue-600 px-5 py-3 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSubmitting ? "Saving..." : "Save changes"}
      </button>
    </form>
  );
}