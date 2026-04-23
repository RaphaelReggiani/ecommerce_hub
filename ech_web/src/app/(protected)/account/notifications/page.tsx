import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { NotificationsList } from "@/features/notifications/components/notifications-list";

export default function NotificationsPage() {
  return (
    <PageContainer>
      <PageTitle
        eyebrow="Account"
        title="Notifications"
        description="Stay updated with your latest activity and system messages."
      />

      <NotificationsList />
    </PageContainer>
  );
}