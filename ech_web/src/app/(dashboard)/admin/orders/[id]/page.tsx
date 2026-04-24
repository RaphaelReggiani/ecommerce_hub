import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";

type AdminOrderDetailPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function AdminOrderDetailPage({
  params,
}: AdminOrderDetailPageProps) {
  const { id } = await params;

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin Orders"
        title="Order detail"
        description={`Review operational details for order ${id}.`}
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400 shadow-xl">
        Admin order detail view will be connected here.
      </div>
    </PageContainer>
  );
}