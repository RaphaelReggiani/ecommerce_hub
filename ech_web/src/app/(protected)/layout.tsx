"use client";

import type { ReactNode } from "react";
import { useSyncExternalStore } from "react";

import { UnauthorizedState } from "@/components/feedback/unauthorized-state";
import { useCurrentUser } from "@/features/users/hooks/use-current-user";

function useIsClient() {
  return useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );
}

export default function ProtectedLayout({
  children,
}: {
  children: ReactNode;
}) {
  const isClient = useIsClient();
  const { data: user, isLoading, isError } = useCurrentUser();

  if (!isClient || isLoading) {
    return (
      <div className="flex min-h-[calc(100vh-140px)] items-center justify-center px-6 py-12 text-slate-400">
        Loading account area...
      </div>
    );
  }

  if (isError || !user) {
    return (
      <div className="px-6 py-12">
        <UnauthorizedState />
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-140px)] bg-black text-white">
      <div className="mx-auto w-full max-w-screen-2xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </div>
    </div>
  );
}