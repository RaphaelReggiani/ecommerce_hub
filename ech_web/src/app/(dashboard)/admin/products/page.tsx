import Link from "next/link";

import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { routes } from "@/config/routes";

export default function AdminProductsPage() {
  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin"
        title="Products"
        description="Manage product catalog, inventory visibility, and product lifecycle."
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
        <Link
          href={routes.admin.createProduct}
          className="inline-flex rounded-2xl bg-blue-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-blue-500"
        >
          Create product
        </Link>
      </div>
    </PageContainer>
  );
}