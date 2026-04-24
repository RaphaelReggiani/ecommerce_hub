import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";

type AdminShippingDetailPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function AdminShippingDetailPage({
  params,
}: AdminShippingDetailPageProps) {
  const { id } = await params;

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin Shipping"
        title="Shipment detail"
        description={`Review shipment ${id}.`}
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400 shadow-xl">
        Admin shipment detail view will be connected here.
      </div>
    </PageContainer>
  );
}