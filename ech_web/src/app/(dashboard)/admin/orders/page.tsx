import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";

export default function AdminOrdersPage() {
  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin"
        title="Orders"
        description="Monitor customer orders and operational order status."
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400 shadow-xl">
        Admin order management table will be connected here.
      </div>
    </PageContainer>
  );
}