import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";

export default function AdminNotificationsPage() {
  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin"
        title="Notifications"
        description="Monitor notification delivery, failed notifications, and retry operations."
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400 shadow-xl">
        Admin notification management table will be connected here.
      </div>
    </PageContainer>
  );
}