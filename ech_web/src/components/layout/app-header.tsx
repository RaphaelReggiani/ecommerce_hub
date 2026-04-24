"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useSyncExternalStore } from "react";

import { routes } from "@/config/routes";
import { NotificationsBell } from "@/features/notifications/components/notifications-bell";
import { canAccessAdmin, canAccessAnalytics } from "@/lib/auth/route-guards";
import { useAuth } from "@/providers/auth-provider";
import { useAppCart } from "@/providers/cart-provider";

function useIsClient() {
  return useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );
}

export function Header() {
  const pathname = usePathname();
  const { itemCount, openCart } = useAppCart();
  const { user, isAuthenticated, logout } = useAuth();
  const isClient = useIsClient();

  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const userRole = user?.role ?? null;
  const canSeeAdmin = canAccessAdmin(userRole) || canAccessAnalytics(userRole);

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  function handleLogout() {
    setIsUserMenuOpen(false);
    logout();
  }

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-black/85 backdrop-blur">
      <div className="mx-auto flex max-w-screen-2xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-3">
          <div className="relative h-11 w-11 overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
            <Image
              src="/images/app_ech.png"
              alt="ECH Innovations"
              fill
              className="object-cover"
              priority
            />
          </div>

          <div className="hidden sm:block">
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-blue-400">
              ECH
            </p>
            <p className="text-sm text-slate-200">ECH Innovations</p>
          </div>
        </Link>

        <nav className="flex items-center gap-2 sm:gap-3">
          <Link
            href={routes.public.products}
            className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
              isActive(routes.public.products)
                ? "bg-slate-900 text-white"
                : "text-slate-300 hover:bg-slate-900 hover:text-white"
            }`}
          >
            Products
          </Link>

          <button
            type="button"
            onClick={openCart}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-950 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
          >
            Cart
            {itemCount > 0 && (
              <span className="inline-flex min-w-6 items-center justify-center rounded-full bg-blue-600 px-2 py-0.5 text-xs font-semibold text-white">
                {itemCount}
              </span>
            )}
          </button>

          {isClient && isAuthenticated ? (
            <>
              <NotificationsBell />

              <div className="relative">
                <button
                  type="button"
                  onClick={() => setIsUserMenuOpen((current) => !current)}
                  className="rounded-xl border border-blue-500/40 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-300 transition hover:bg-blue-500 hover:text-white"
                >
                  Welcome, {user?.user_name ?? user?.email}
                </button>

                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-3 w-64 overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 shadow-2xl">
                    <div className="border-b border-slate-800 px-4 py-3">
                      <p className="text-sm font-medium text-white">
                        {user?.user_name ?? "Account"}
                      </p>
                      <p className="truncate text-xs text-slate-400">
                        {user?.email}
                      </p>
                    </div>

                    <div className="p-2">
                      <Link
                        href={routes.protected.account}
                        onClick={() => setIsUserMenuOpen(false)}
                        className="block rounded-xl px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-900 hover:text-white"
                      >
                        Account
                      </Link>

                      <Link
                        href={routes.protected.profile}
                        onClick={() => setIsUserMenuOpen(false)}
                        className="block rounded-xl px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-900 hover:text-white"
                      >
                        Profile
                      </Link>

                      <Link
                        href={routes.protected.orders}
                        onClick={() => setIsUserMenuOpen(false)}
                        className="block rounded-xl px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-900 hover:text-white"
                      >
                        Orders
                      </Link>

                      <Link
                        href={routes.protected.payments}
                        onClick={() => setIsUserMenuOpen(false)}
                        className="block rounded-xl px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-900 hover:text-white"
                      >
                        Payments
                      </Link>

                      <Link
                        href={routes.protected.shipping}
                        onClick={() => setIsUserMenuOpen(false)}
                        className="block rounded-xl px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-900 hover:text-white"
                      >
                        Shipping
                      </Link>

                      <Link
                        href={routes.protected.notifications}
                        onClick={() => setIsUserMenuOpen(false)}
                        className="block rounded-xl px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-900 hover:text-white"
                      >
                        Notifications
                      </Link>

                      <Link
                        href={routes.protected.reviews}
                        onClick={() => setIsUserMenuOpen(false)}
                        className="block rounded-xl px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-900 hover:text-white"
                      >
                        Reviews
                      </Link>

                      {canSeeAdmin && (
                        <Link
                          href={routes.admin.home}
                          onClick={() => setIsUserMenuOpen(false)}
                          className="mt-2 block rounded-xl border border-blue-500/30 bg-blue-500/10 px-3 py-2 text-sm text-blue-300 transition hover:bg-blue-500 hover:text-white"
                        >
                          Admin dashboard
                        </Link>
                      )}

                      <button
                        type="button"
                        onClick={handleLogout}
                        className="mt-2 w-full rounded-xl px-3 py-2 text-left text-sm text-red-300 transition hover:bg-red-500/10 hover:text-red-200"
                      >
                        Logout
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href={routes.public.login}
                className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
                  isActive(routes.public.login)
                    ? "bg-slate-900 text-white"
                    : "text-slate-300 hover:bg-slate-900 hover:text-white"
                }`}
              >
                Login
              </Link>

              <Link
                href={routes.public.register}
                className="rounded-xl border border-blue-500/40 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-300 transition hover:bg-blue-500 hover:text-white"
              >
                Create account
              </Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}