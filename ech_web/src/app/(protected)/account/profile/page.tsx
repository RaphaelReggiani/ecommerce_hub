"use client";

import Link from "next/link";

import { useCurrentUser } from "@/features/users/hooks/use-current-user";

const accountLinks = [
  {
    title: "Profile",
    description: "Update your personal information and account data.",
    href: "/account/profile",
  },
  {
    title: "Orders",
    description: "View your order history and follow each order lifecycle.",
    href: "/account/orders",
  },
  {
    title: "Cart",
    description: "Review the products currently selected for purchase.",
    href: "/cart",
  },
  {
    title: "Checkout",
    description: "Proceed with address confirmation and order placement.",
    href: "/checkout",
  },
];

export default function AccountPage() {
  const { data: user, isLoading } = useCurrentUser();

  if (isLoading) {
    return (
      <div className="flex justify-center py-20 text-slate-400">
        Loading account...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 p-8 shadow-2xl lg:p-10">
        <div className="space-y-4">
          <span className="inline-flex rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-xs font-medium uppercase tracking-[0.24em] text-blue-400">
            My account
          </span>

          <h1 className="text-3xl font-semibold text-white md:text-4xl">
            Welcome back{user?.user_name ? `, ${user.user_name}` : ""}
          </h1>

          <p className="max-w-3xl text-sm leading-8 text-slate-300 md:text-base">
            Manage your profile, review your orders, and continue your shopping
            journey through the E-Commerce Hub customer area.
          </p>
        </div>
      </section>

      <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {accountLinks.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="group rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl transition hover:-translate-y-1 hover:border-blue-500/40 hover:bg-slate-900"
          >
            <p className="text-xs font-medium uppercase tracking-[0.24em] text-slate-500">
              Account
            </p>

            <h2 className="mt-3 text-2xl font-semibold text-white transition group-hover:text-blue-300">
              {item.title}
            </h2>

            <p className="mt-3 text-sm leading-7 text-slate-400">
              {item.description}
            </p>

            <div className="mt-6 inline-flex rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition group-hover:border-blue-500 group-hover:text-white">
              Open section
            </div>
          </Link>
        ))}
      </section>
    </div>
  );
}