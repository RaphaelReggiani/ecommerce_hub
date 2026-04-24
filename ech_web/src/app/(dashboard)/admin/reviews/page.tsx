import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";

export default function AdminReviewsPage() {
  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin"
        title="Reviews"
        description="Moderate customer reviews and monitor review status."
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400 shadow-xl">
        Admin review moderation table will be connected here.
      </div>
    </PageContainer>
  );
}