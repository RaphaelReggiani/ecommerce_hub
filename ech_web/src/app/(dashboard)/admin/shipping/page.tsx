import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";

export default function AdminShippingPage() {
  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin"
        title="Shipping"
        description="Monitor shipments, delivery status, and logistics operations."
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400 shadow-xl">
        Admin shipping management table will be connected here.
      </div>
    </PageContainer>
  );
}