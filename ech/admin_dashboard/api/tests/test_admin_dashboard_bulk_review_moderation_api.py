import uuid
from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardReviewBulkModerationException,
)
from ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service import (
    AdminDashboardBulkReviewModerationService,
)
from ech.users.models import CustomUser


class AdminDashboardBulkReviewModerationApiTestCase(APITestCase):
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

        cls.admin = CustomUser.objects.create_user(
            email="admin@company.com",
            password="StrongPassword123",
            user_name="Admin User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

        cls.url = reverse(
            "admin-dashboard-api:admin-dashboard-bulk-review-moderation"
        )

        cls.review_id_1 = uuid.UUID("11111111-1111-1111-1111-111111111111")
        cls.review_id_2 = uuid.UUID("22222222-2222-2222-2222-222222222222")

        cls.valid_payload = {
            "moderation_action": "approve",
            "review_ids": [
                str(cls.review_id_1),
                str(cls.review_id_2),
            ],
            "reason": "Bulk approval by admin dashboard.",
        }

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_bulk_review_moderation_requires_authentication(self):
        """Reject bulk review moderation for unauthenticated users."""
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_bulk_review_moderation_rejects_customer_user(self):
        """Reject bulk review moderation for customer users."""
        self.authenticate(self.customer)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bulk_review_moderation_rejects_operations_staff(self):
        """Reject bulk review moderation for operations staff."""
        self.authenticate(self.operations_staff)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(
        AdminDashboardBulkReviewModerationService,
        "execute_bulk_moderation",
    )
    def test_bulk_review_moderation_allows_support_staff(
        self,
        mocked_service,
    ):
        """Allow support staff to execute bulk review moderation."""
        mocked_service.return_value = {
            "moderation_action": "approve",
            "processed_reviews": [
                self.review_id_1,
                self.review_id_2,
            ],
            "total_processed": 2,
        }

        self.authenticate(self.support_staff)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("moderation_action", response.data)
        self.assertIn("processed_reviews", response.data)
        self.assertIn("total_processed", response.data)

        mocked_service.assert_called_once_with(
            moderation_action="approve",
            review_ids=[
                self.review_id_1,
                self.review_id_2,
            ],
            performed_by=self.support_staff,
            reason="Bulk approval by admin dashboard.",
        )

    @patch.object(
        AdminDashboardBulkReviewModerationService,
        "execute_bulk_moderation",
    )
    def test_bulk_review_moderation_allows_admin(
        self,
        mocked_service,
    ):
        """Allow admin users to execute bulk review moderation."""
        mocked_service.return_value = {
            "moderation_action": "approve",
            "processed_reviews": [
                self.review_id_1,
            ],
            "total_processed": 1,
        }

        self.authenticate(self.admin)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mocked_service.assert_called_once_with(
            moderation_action="approve",
            review_ids=[
                self.review_id_1,
                self.review_id_2,
            ],
            performed_by=self.admin,
            reason="Bulk approval by admin dashboard.",
        )

    def test_bulk_review_moderation_rejects_invalid_action(self):
        """Reject payloads with invalid moderation action."""
        self.authenticate(self.admin)

        payload = {
            "moderation_action": "invalid_action",
            "review_ids": self.valid_payload["review_ids"],
            "reason": self.valid_payload["reason"],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("moderation_action", response.data)

    def test_bulk_review_moderation_requires_review_ids(self):
        """Reject payloads without review IDs."""
        self.authenticate(self.admin)

        payload = {
            "moderation_action": "approve",
            "review_ids": [],
            "reason": self.valid_payload["reason"],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("review_ids", response.data)

    def test_bulk_review_moderation_rejects_invalid_review_id(self):
        """Reject payloads with invalid review UUID."""
        self.authenticate(self.admin)

        payload = {
            "moderation_action": "approve",
            "review_ids": ["invalid-uuid"],
            "reason": self.valid_payload["reason"],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("review_ids", response.data)

    @patch.object(
        AdminDashboardBulkReviewModerationService,
        "execute_bulk_moderation",
        side_effect=AdminDashboardReviewBulkModerationException(),
    )
    def test_bulk_review_moderation_returns_400_when_service_fails(
        self,
        mocked_service,
    ):
        """Return 400 when bulk review moderation service raises handled exception."""
        self.authenticate(self.admin)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

        mocked_service.assert_called_once_with(
            moderation_action="approve",
            review_ids=[
                self.review_id_1,
                self.review_id_2,
            ],
            performed_by=self.admin,
            reason="Bulk approval by admin dashboard.",
        )

    @patch.object(
        AdminDashboardBulkReviewModerationService,
        "execute_bulk_moderation",
    )
    def test_bulk_review_moderation_allows_blank_reason(
        self,
        mocked_service,
    ):
        """Allow blank reason in bulk review moderation payload."""
        mocked_service.return_value = {
            "moderation_action": "hide",
            "processed_reviews": [
                self.review_id_1,
            ],
            "total_processed": 1,
        }

        payload = {
            "moderation_action": "hide",
            "review_ids": [str(self.review_id_1)],
            "reason": "",
        }

        self.authenticate(self.admin)

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mocked_service.assert_called_once_with(
            moderation_action="hide",
            review_ids=[self.review_id_1],
            performed_by=self.admin,
            reason="",
        )