import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";

type AdminPaymentDetailPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function AdminPaymentDetailPage({
  params,
}: AdminPaymentDetailPageProps) {
  const { id } = await params;

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin Payments"
        title="Payment detail"
        description={`Review payment ${id}.`}
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400 shadow-xl">
        Admin payment detail view will be connected here.
      </div>
    </PageContainer>
  );
}