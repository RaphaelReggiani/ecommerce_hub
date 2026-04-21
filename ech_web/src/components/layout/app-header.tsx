"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAppCart } from "@/providers/cart-provider";

export function Header() {
  const pathname = usePathname();
  const { itemCount, openCart } = useAppCart();

  const isActive = (href: string) => {
    if (href === "/") {
      return pathname === "/";
    }

    return pathname.startsWith(href);
  };

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
            href="/products"
            className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
              isActive("/products")
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

          <Link
            href="/login"
            className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
              isActive("/login")
                ? "bg-slate-900 text-white"
                : "text-slate-300 hover:bg-slate-900 hover:text-white"
            }`}
          >
            Login
          </Link>

          <Link
            href="/register"
            className="rounded-xl border border-blue-500/40 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-300 transition hover:bg-blue-500 hover:text-white"
          >
            Create account
          </Link>
        </nav>
      </div>
    </header>
  );
}