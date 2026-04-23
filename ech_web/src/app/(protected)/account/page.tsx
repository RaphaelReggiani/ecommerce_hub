import Link from "next/link";

import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { routes } from "@/config/routes";

const accountSections = [
  {
    title: "Profile",
    description: "Manage your personal information and account details.",
    href: routes.protected.profile,
    cta: "Open profile",
  },
  {
    title: "Orders",
    description: "Track your orders and review the lifecycle of each purchase.",
    href: routes.protected.orders,
    cta: "View orders",
  },
  {
    title: "Payments",
    description: "Review your payment history and payment transaction details.",
    href: routes.protected.payments,
    cta: "View payments",
  },
  {
    title: "Shipping",
    description: "Follow shipment progress and delivery status updates.",
    href: routes.protected.shipping,
    cta: "View shipping",
  },
  {
    title: "Notifications",
    description: "Check your latest account and order-related notifications.",
    href: routes.protected.notifications,
    cta: "View notifications",
  },
  {
    title: "Reviews",
    description: "Manage your submitted reviews and product feedback.",
    href: routes.protected.reviews,
    cta: "View reviews",
  },
] as const;

export default function AccountHomePage() {
  return (
    <PageContainer>
      <PageTitle
        eyebrow="Account"
        title="Your account"
        description="Access your customer area, manage your information, and follow your activity across the platform."
      />

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {accountSections.map((section) => (
          <Link
            key={section.href}
            href={section.href}
            className="group rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl transition hover:border-blue-500/40 hover:bg-slate-900"
          >
            <div className="mb-5">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                Account
              </p>
              <h2 className="mt-3 text-xl font-semibold text-white transition group-hover:text-blue-300">
                {section.title}
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-400">
                {section.description}
              </p>
            </div>

            <span className="inline-flex items-center rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition group-hover:border-blue-500 group-hover:text-white">
              {section.cta}
            </span>
          </Link>
        ))}
      </div>
    </PageContainer>
  );
}