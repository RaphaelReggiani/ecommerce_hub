"use client";

import { ProfileForm } from "@/features/users/components/profile-form";
import { useProfile } from "@/features/users/hooks/use-profile";
import { useUpdateProfile } from "@/features/users/hooks/use-update-profile";
import type { ProfileSchemaValues } from "@/features/users/schemas/profile-schema";

export default function ProfilePage() {
  const { data: profile, isLoading } = useProfile();
  const updateProfileMutation = useUpdateProfile();

  async function handleSubmit(values: ProfileSchemaValues) {
    await updateProfileMutation.mutateAsync(values);
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-20 text-slate-400">
        Loading profile...
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="flex justify-center py-20 text-slate-400">
        Unable to load profile.
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-white">Your profile</h1>
        <p className="mt-2 text-sm text-slate-400">
          Update your account information
        </p>
      </div>

      <ProfileForm
        initialValues={profile}
        onSubmit={handleSubmit}
      />
    </div>
  );
}