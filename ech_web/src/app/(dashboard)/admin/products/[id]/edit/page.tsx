import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";

type AdminEditProductPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function AdminEditProductPage({
  params,
}: AdminEditProductPageProps) {
  const { id } = await params;

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin Products"
        title="Edit product"
        description={`Editing product ${id}.`}
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400 shadow-xl">
        Product edit form will be connected here.
      </div>
    </PageContainer>
  );
}