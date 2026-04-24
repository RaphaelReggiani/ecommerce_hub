"use client";

import type { ReactNode } from "react";
import { usePathname } from "next/navigation";
import { useSyncExternalStore } from "react";

import { UnauthorizedState } from "@/components/feedback/unauthorized-state";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { Breadcrumb } from "@/components/layout/breadcrumb";
import { useCurrentUser } from "@/features/users/hooks/use-current-user";
import { evaluateRouteAccess } from "@/lib/auth/route-guards";

function useIsClient() {
  return useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );
}

export default function DashboardLayout({
  children,
}: {
  children: ReactNode;
}) {
  const pathname = usePathname();
  const isClient = useIsClient();
  const { data: user, isLoading, isError } = useCurrentUser();

  const isAuthenticated = Boolean(user);

  const access = evaluateRouteAccess({
    pathname,
    user: user
      ? {
          role: user.role,
        }
      : null,
    isAuthenticated,
  });

  if (!isClient || isLoading) {
    return (
      <div className="flex min-h-[calc(100vh-140px)] items-center justify-center px-6 py-12 text-slate-400">
        Loading admin area...
      </div>
    );
  }

  if (isError || !user || !access.allowed) {
    return (
      <div className="min-h-[calc(100vh-140px)] bg-black px-6 py-12">
        <UnauthorizedState />
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-140px)] bg-black text-white">
      <div className="mx-auto flex w-full max-w-screen-2xl gap-8 px-4 py-8 sm:px-6 lg:px-8">
        <AppSidebar userRole={user.role} />

        <main className="min-w-0 flex-1 space-y-6">
          <Breadcrumb />
          {children}
        </main>
      </div>
    </div>
  );
}