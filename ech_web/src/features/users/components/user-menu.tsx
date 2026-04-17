"use client";

import { useLogout } from "@/features/users/hooks/use-logout";
import { useAuth } from "@/providers/auth-provider";

export function UserMenu() {
  const { user } = useAuth();
  const logoutMutation = useLogout();

  if (!user) {
    return null;
  }

  return (
    <div className="flex items-center gap-3 rounded-2xl border border-slate-800 bg-black px-4 py-3">
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white">
        {user.user_name?.charAt(0)?.toUpperCase() || "U"}
      </div>

      <div className="min-w-0">
        <p className="truncate text-sm font-medium text-white">{user.user_name}</p>
        <p className="truncate text-xs text-slate-400">{user.email}</p>
      </div>

      <button
        type="button"
        onClick={() => logoutMutation.mutate()}
        disabled={logoutMutation.isPending}
        className="ml-2 rounded-xl border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-60"
      >
        {logoutMutation.isPending ? "Signing out..." : "Logout"}
      </button>
    </div>
  );
}