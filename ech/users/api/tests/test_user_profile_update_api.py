from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserProfileUpdateApiTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/v1/users/profile/"

        self.user = User.objects.create_user(
            email="user@test.com",
            password="StrongPassword123",
            user_name="Original Name",
            user_phone="111111111",
            user_country="Brazil",
            user_state="SP",
            user_address="Old Address",
            user_age=30,
            is_active=True,
            email_confirmed=True,
        )

        self.unconfirmed_user = User.objects.create_user(
            email="unconfirmed@test.com",
            password="StrongPassword123",
            user_name="Unconfirmed User",
            is_active=True,
            email_confirmed=False,
        )

    def test_profile_update_success(self):
        """
        Authenticated confirmed user must be able to update profile fields.
        """

        self.client.force_authenticate(user=self.user)

        payload = {
            "user_name": "Updated Name",
            "user_phone": "999999999",
            "user_country": "USA",
            "user_state": "CA",
            "user_address": "New Address",
            "user_age": 35,
        }

        response = self.client.patch(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertEqual(self.user.user_name, "Updated Name")
        self.assertEqual(self.user.user_phone, "999999999")
        self.assertEqual(self.user.user_country, "USA")
        self.assertEqual(self.user.user_state, "CA")
        self.assertEqual(self.user.user_address, "New Address")
        self.assertEqual(self.user.user_age, 35)

        self.assertEqual(response.data["user_name"], "Updated Name")
        self.assertEqual(response.data["user_phone"], "999999999")
        self.assertEqual(response.data["user_country"], "USA")
        self.assertEqual(response.data["user_state"], "CA")
        self.assertEqual(response.data["user_address"], "New Address")
        self.assertEqual(response.data["user_age"], 35)

    def test_profile_update_partial_success(self):
        """
        Partial profile update must update only provided fields.
        """

        self.client.force_authenticate(user=self.user)

        payload = {
            "user_name": "Partial Update",
        }

        response = self.client.patch(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertEqual(self.user.user_name, "Partial Update")
        self.assertEqual(self.user.user_phone, "111111111")
        self.assertEqual(self.user.user_country, "Brazil")

    def test_profile_update_requires_authentication(self):
        """
        Unauthenticated user must not update profile.
        """

        payload = {
            "user_name": "Blocked Update",
        }

        response = self.client.patch(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_update_requires_confirmed_email(self):
        """
        Authenticated but unconfirmed user must not update profile.
        """

        self.client.force_authenticate(user=self.unconfirmed_user)

        payload = {
            "user_name": "Blocked Update",
        }

        response = self.client.patch(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_update_ignores_non_editable_fields(self):
        """
        Non-editable fields must not be changed through profile update.
        """

        self.client.force_authenticate(user=self.user)

        payload = {
            "user_email": "newemail@test.com",
            "user_role": "admin",
            "user_name": "Allowed Change",
        }

        response = self.client.patch(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertEqual(self.user.user_email, "user@test.com")
        self.assertEqual(self.user.user_role, User.ROLE_CUSTOMER_USER)
        self.assertEqual(self.user.user_name, "Allowed Change")

    def test_profile_update_invalid_age_returns_400(self):
        """
        Invalid profile field values must return 400 response.
        """

        self.client.force_authenticate(user=self.user)

        payload = {
            "user_age": -1,
        }

        response = self.client.patch(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user_age", response.data)

    def test_profile_update_empty_payload_returns_current_profile(self):
        """
        Empty partial update must return 200 and keep current profile unchanged.
        """

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertEqual(self.user.user_name, "Original Name")
        self.assertEqual(self.user.user_phone, "111111111")
        self.assertEqual(response.data["user_name"], "Original Name")