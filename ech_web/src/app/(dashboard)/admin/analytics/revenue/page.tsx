import { redirect } from "next/navigation";

import { routes } from "@/config/routes";

export default function AnalyticsRevenuePage() {
  redirect(routes.admin.analyticsSales);
}