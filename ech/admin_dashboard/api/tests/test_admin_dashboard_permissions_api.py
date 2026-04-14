from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser


class AdminDashboardPermissionsApiTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        cls.analytics_staff = CustomUser.objects.create_user(
            email="analytics@company.com",
            password="StrongPassword123",
            user_name="Analytics Staff",
            role=CustomUser.ROLE_ANALYTICS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        cls.operations_staff = CustomUser.objects.create_user(
            email="operations@company.com",
            password="StrongPassword123",
            user_name="Operations Staff",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        cls.support_staff = CustomUser.objects.create_user(
            email="support@company.com",
            password="StrongPassword123",
            user_name="Support Staff",
            role=CustomUser.ROLE_SUPPORT_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        cls.payment_staff = CustomUser.objects.create_user(
            email="payments@company.com",
            password="StrongPassword123",
            user_name="Payment Staff",
            role=CustomUser.ROLE_PAYMENT_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        cls.admin = CustomUser.objects.create_user(
            email="admin@company.com",
            password="StrongPassword123",
            user_name="Admin User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

        cls.superadmin = CustomUser.objects.create_user(
            email="superadmin@company.com",
            password="StrongPassword123",
            user_name="Superadmin User",
            role=CustomUser.ROLE_SUPERADMIN,
            is_active=True,
            email_confirmed=True,
        )

        cls.summary_url = reverse(
            "admin-dashboard-api:admin-dashboard-summary"
        )
        cls.metrics_url = reverse(
            "admin-dashboard-api:admin-dashboard-operational-metrics"
        )
        cls.activity_url = reverse(
            "admin-dashboard-api:admin-dashboard-activity"
        )
        cls.alerts_url = reverse(
            "admin-dashboard-api:admin-dashboard-alerts"
        )
        cls.bulk_order_url = reverse(
            "admin-dashboard-api:admin-dashboard-bulk-order-action"
        )
        cls.bulk_review_url = reverse(
            "admin-dashboard-api:admin-dashboard-bulk-review-moderation"
        )
        cls.notification_retry_url = reverse(
            "admin-dashboard-api:admin-dashboard-notification-retry"
        )

        cls.valid_bulk_order_payload = {
            "action_type": "mark_processing",
            "order_ids": [
                "11111111-1111-1111-1111-111111111111",
            ],
        }

        cls.valid_bulk_review_payload = {
            "moderation_action": "approve",
            "review_ids": [
                "11111111-1111-1111-1111-111111111111",
            ],
            "reason": "Bulk moderation test.",
        }

        cls.valid_notification_retry_payload = {
            "notification_ids": [
                "11111111-1111-1111-1111-111111111111",
            ],
        }

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_summary_service.AdminDashboardSummaryService.get_summary"
    )
    def test_dashboard_summary_permission_matrix(self, mocked_service):
        """Allow only dashboard-access roles to retrieve summary."""
        mocked_service.return_value = {
            "orders": {
                "total_orders": 0,
                "pending_orders": 0,
                "processing_orders": 0,
                "shipped_orders": 0,
                "delivered_orders": 0,
                "cancelled_orders": 0,
            },
            "payments": {
                "total_payments": 0,
                "captured_payments": 0,
                "failed_payments": 0,
                "refunded_payments": 0,
                "partially_refunded_payments": 0,
            },
            "shipping": {
                "total_shipments": 0,
                "pending_shipments": 0,
                "in_transit_shipments": 0,
                "delivered_shipments": 0,
                "failed_shipments": 0,
                "returned_shipments": 0,
            },
            "users": {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "staff_users": 0,
                "customer_users": 0,
                "confirmed_users": 0,
                "unconfirmed_users": 0,
            },
            "reviews": {
                "total_reviews": 0,
                "pending_reviews": 0,
                "approved_reviews": 0,
                "rejected_reviews": 0,
                "hidden_reviews": 0,
                "cancelled_reviews": 0,
            },
            "products": {
                "total_products": 0,
                "active_products": 0,
                "inactive_products": 0,
            },
        }

        allowed_users = [
            self.analytics_staff,
            self.operations_staff,
            self.support_staff,
            self.payment_staff,
            self.admin,
            self.superadmin,
        ]
        denied_users = [
            self.customer,
        ]

        for user in allowed_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.get(self.summary_url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

        for user in denied_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.get(self.summary_url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service.AdminDashboardOperationalMetricsService.get_operational_metrics"
    )
    def test_dashboard_operational_metrics_permission_matrix(
        self,
        mocked_service,
    ):
        """Allow only dashboard-access roles to retrieve operational metrics."""
        mocked_service.return_value = {
            "orders": {
                "pending_orders": 0,
                "processing_orders": 0,
                "cancelled_orders": 0,
            },
            "payments": {
                "failed_payments": 0,
                "processing_payments": 0,
                "refunded_payments": 0,
            },
            "shipping": {
                "delayed_shipments": 0,
                "failed_shipments": 0,
                "in_transit_shipments": 0,
            },
            "reviews": {
                "pending_moderation": 0,
                "flagged_reviews": 0,
                "hidden_reviews": 0,
            },
            "notifications": {
                "failed_notifications": 0,
                "pending_notifications": 0,
                "unread_notifications": 0,
            },
            "products": {
                "low_stock_products": 0,
                "out_of_stock_products": 0,
                "products_without_images": 0,
            },
        }

        allowed_users = [
            self.analytics_staff,
            self.operations_staff,
            self.support_staff,
            self.payment_staff,
            self.admin,
            self.superadmin,
        ]
        denied_users = [
            self.customer,
        ]

        for user in allowed_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.get(self.metrics_url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

        for user in denied_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.get(self.metrics_url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_recent_activity_service.AdminDashboardRecentActivityService.get_recent_activity"
    )
    def test_dashboard_recent_activity_permission_matrix(
        self,
        mocked_service,
    ):
        """Allow only dashboard-access roles to retrieve recent activity."""
        mocked_service.return_value = {
            "activities": [],
            "total": 0,
            "limit": 50,
        }

        allowed_users = [
            self.analytics_staff,
            self.operations_staff,
            self.support_staff,
            self.payment_staff,
            self.admin,
            self.superadmin,
        ]
        denied_users = [
            self.customer,
        ]

        for user in allowed_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.get(self.activity_url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

        for user in denied_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.get(self.activity_url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_alerts_service.AdminDashboardAlertsService.get_alerts"
    )
    def test_dashboard_alerts_permission_matrix(self, mocked_service):
        """Allow only dashboard-access roles to retrieve alerts."""
        mocked_service.return_value = {
            "alerts": [],
            "total_alerts": 0,
            "critical_alerts": 0,
            "warning_alerts": 0,
            "info_alerts": 0,
        }

        allowed_users = [
            self.analytics_staff,
            self.operations_staff,
            self.support_staff,
            self.payment_staff,
            self.admin,
            self.superadmin,
        ]
        denied_users = [
            self.customer,
        ]

        for user in allowed_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.get(self.alerts_url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

        for user in denied_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.get(self.alerts_url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.AdminDashboardBulkOrderActionsService.execute_bulk_action"
    )
    def test_bulk_order_action_permission_matrix(self, mocked_service):
        """Allow only superadmin, admin, and operations staff to execute bulk order actions."""
        mocked_service.return_value = {
            "action": "mark_processing",
            "processed_orders": [
                "11111111-1111-1111-1111-111111111111",
            ],
            "total_processed": 1,
        }

        allowed_users = [
            self.operations_staff,
            self.admin,
            self.superadmin,
        ]
        denied_users = [
            self.customer,
            self.analytics_staff,
            self.support_staff,
            self.payment_staff,
        ]

        for user in allowed_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.post(
                    self.bulk_order_url,
                    self.valid_bulk_order_payload,
                    format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)

        for user in denied_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.post(
                    self.bulk_order_url,
                    self.valid_bulk_order_payload,
                    format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.AdminDashboardBulkReviewModerationService.execute_bulk_moderation"
    )
    def test_bulk_review_moderation_permission_matrix(
        self,
        mocked_service,
    ):
        """Allow only superadmin, admin, and support staff to execute bulk review moderation."""
        mocked_service.return_value = {
            "moderation_action": "approve",
            "processed_reviews": [
                "11111111-1111-1111-1111-111111111111",
            ],
            "total_processed": 1,
        }

        allowed_users = [
            self.support_staff,
            self.admin,
            self.superadmin,
        ]
        denied_users = [
            self.customer,
            self.analytics_staff,
            self.operations_staff,
            self.payment_staff,
        ]

        for user in allowed_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.post(
                    self.bulk_review_url,
                    self.valid_bulk_review_payload,
                    format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)

        for user in denied_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.post(
                    self.bulk_review_url,
                    self.valid_bulk_review_payload,
                    format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.AdminDashboardBulkNotificationRetryService.retry_notifications"
    )
    def test_bulk_notification_retry_permission_matrix(
        self,
        mocked_service,
    ):
        """Allow only superadmin, admin, and support staff to retry notifications."""
        mocked_service.return_value = {
            "retried_notifications": [
                "11111111-1111-1111-1111-111111111111",
            ],
            "total_retried": 1,
        }

        allowed_users = [
            self.support_staff,
            self.admin,
            self.superadmin,
        ]
        denied_users = [
            self.customer,
            self.analytics_staff,
            self.operations_staff,
            self.payment_staff,
        ]

        for user in allowed_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.post(
                    self.notification_retry_url,
                    self.valid_notification_retry_payload,
                    format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)

        for user in denied_users:
            with self.subTest(user=user.user_role):
                self.authenticate(user)
                response = self.client.post(
                    self.notification_retry_url,
                    self.valid_notification_retry_payload,
                    format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dashboard_endpoints_require_authentication(self):
        """Reject unauthenticated access to all dashboard GET endpoints."""
        urls = [
            self.summary_url,
            self.metrics_url,
            self.activity_url,
            self.alerts_url,
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn(
                    response.status_code,
                    {
                        status.HTTP_401_UNAUTHORIZED,
                        status.HTTP_403_FORBIDDEN,
                    },
                )

    def test_bulk_operation_endpoints_require_authentication(self):
        """Reject unauthenticated access to all bulk operation POST endpoints."""
        payloads = [
            (self.bulk_order_url, self.valid_bulk_order_payload),
            (self.bulk_review_url, self.valid_bulk_review_payload),
            (
                self.notification_retry_url,
                self.valid_notification_retry_payload,
            ),
        ]

        for url, payload in payloads:
            with self.subTest(url=url):
                response = self.client.post(url, payload, format="json")
                self.assertIn(
                    response.status_code,
                    {
                        status.HTTP_401_UNAUTHORIZED,
                        status.HTTP_403_FORBIDDEN,
                    },
                )