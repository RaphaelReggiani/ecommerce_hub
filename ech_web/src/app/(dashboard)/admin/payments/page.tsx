import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";

export default function AdminPaymentsPage() {
  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin"
        title="Payments"
        description="Monitor payment lifecycle, refunds, and failed transactions."
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400 shadow-xl">
        Admin payment management table will be connected here.
      </div>
    </PageContainer>
  );
}