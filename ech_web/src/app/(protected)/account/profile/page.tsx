"use client";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { useCurrentUser } from "@/features/users/hooks/use-current-user";

export default function ProfilePage() {
  const { data: user, isLoading, isError, refetch } = useCurrentUser();

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState
          title="Loading profile..."
          description="Please wait while we load your account details."
        />
      </PageContainer>
    );
  }

  if (isError || !user) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load profile."
          description="We could not retrieve your profile information right now."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Profile"
        title="Your profile"
        description="Review your account information and customer access details."
      />

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            User name
          </p>
          <p className="mt-3 text-lg font-medium text-white">
            {user.user_name || "-"}
          </p>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Email
          </p>
          <p className="mt-3 text-lg font-medium text-white">
            {user.email || "-"}
          </p>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Email confirmed
          </p>
          <p className="mt-3 text-lg font-medium text-white">
            {user.email_confirmed ? "Yes" : "No"}
          </p>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Active account
          </p>
          <p className="mt-3 text-lg font-medium text-white">
            {user.is_active ? "Yes" : "No"}
          </p>
        </div>
      </div>
    </PageContainer>
  );
}