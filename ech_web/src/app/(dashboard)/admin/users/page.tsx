import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";

export default function AdminUsersPage() {
  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin"
        title="Users"
        description="Monitor platform users, staff access, and customer accounts."
      />

      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400 shadow-xl">
        Admin user management table will be connected here.
      </div>
    </PageContainer>
  );
}