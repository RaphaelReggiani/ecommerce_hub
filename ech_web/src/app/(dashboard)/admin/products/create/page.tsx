import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";

export default function AdminCreateProductPage() {
  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin Products"
        title="Create product"
        description="Create a new product for the E-Commerce Hub catalog."
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400 shadow-xl">
        Product creation form will be connected here.
      </div>
    </PageContainer>
  );
}