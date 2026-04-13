from django.core.cache import cache
from django.test import TestCase

from ech.admin_dashboard.services.admin_dashboard_summary_service import (
    AdminDashboardSummaryService,
)
from ech.admin_dashboard.services.admin_dashboard_operational_metrics_service import (
    AdminDashboardOperationalMetricsService,
)
from ech.admin_dashboard.services.admin_dashboard_recent_activity_service import (
    AdminDashboardRecentActivityService,
)
from ech.admin_dashboard.services.admin_dashboard_alerts_service import (
    AdminDashboardAlertsService,
)
from ech.admin_dashboard.services.cache_service import (
    AdminDashboardCacheService,
)
from ech.users.models import CustomUser


class AdminDashboardCacheInvalidationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = CustomUser.objects.create_user(
            email="admin@company.com",
            password="StrongPassword123",
            user_name="Admin User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

    def setUp(self):
        cache.clear()

    def test_dashboard_summary_cache_invalidated_after_version_bump(self):
        """Invalidate cached dashboard summary after dashboard cache invalidation."""
        summary_first = AdminDashboardSummaryService.get_summary(
            performed_by=self.admin
        )

        AdminDashboardCacheService.invalidate_dashboard_cache()

        summary_second = AdminDashboardSummaryService.get_summary(
            performed_by=self.admin
        )

        self.assertIsNotNone(summary_first)
        self.assertIsNotNone(summary_second)

    def test_operational_metrics_cache_invalidated_after_version_bump(self):
        """Invalidate cached operational metrics after operational metrics cache invalidation."""
        metrics_first = (
            AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=self.admin
            )
        )

        AdminDashboardCacheService.invalidate_operational_metrics_cache()

        metrics_second = (
            AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=self.admin
            )
        )

        self.assertIsNotNone(metrics_first)
        self.assertIsNotNone(metrics_second)

    def test_recent_activity_cache_invalidated_after_version_bump(self):
        """Invalidate cached recent activity feed after activity cache invalidation."""
        activity_first = AdminDashboardRecentActivityService.get_recent_activity(
            limit=10,
            performed_by=self.admin,
        )

        AdminDashboardCacheService.invalidate_activity_feed_cache()

        activity_second = AdminDashboardRecentActivityService.get_recent_activity(
            limit=10,
            performed_by=self.admin,
        )

        self.assertIsNotNone(activity_first)
        self.assertIsNotNone(activity_second)

    def test_alerts_cache_invalidated_after_version_bump(self):
        """Invalidate cached alerts after alerts cache invalidation."""
        alerts_first = AdminDashboardAlertsService.get_alerts(
            performed_by=self.admin
        )

        AdminDashboardCacheService.invalidate_alerts_cache()

        alerts_second = AdminDashboardAlertsService.get_alerts(
            performed_by=self.admin
        )

        self.assertIsNotNone(alerts_first)
        self.assertIsNotNone(alerts_second)

    def test_invalidate_all_dashboard_views_bumps_all_versions(self):
        """Invalidate all dashboard cache namespaces simultaneously."""
        summary_first = AdminDashboardSummaryService.get_summary(
            performed_by=self.admin
        )

        metrics_first = (
            AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=self.admin
            )
        )

        activity_first = AdminDashboardRecentActivityService.get_recent_activity(
            performed_by=self.admin
        )

        alerts_first = AdminDashboardAlertsService.get_alerts(
            performed_by=self.admin
        )

        AdminDashboardCacheService.invalidate_all_dashboard_views()

        summary_second = AdminDashboardSummaryService.get_summary(
            performed_by=self.admin
        )

        metrics_second = (
            AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=self.admin
            )
        )

        activity_second = AdminDashboardRecentActivityService.get_recent_activity(
            performed_by=self.admin
        )

        alerts_second = AdminDashboardAlertsService.get_alerts(
            performed_by=self.admin
        )

        self.assertIsNotNone(summary_first)
        self.assertIsNotNone(summary_second)

        self.assertIsNotNone(metrics_first)
        self.assertIsNotNone(metrics_second)

        self.assertIsNotNone(activity_first)
        self.assertIsNotNone(activity_second)

        self.assertIsNotNone(alerts_first)
        self.assertIsNotNone(alerts_second)