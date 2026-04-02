from django.core import mail
from django.core.cache import cache
from django.urls import reverse
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from ech.users.models import CustomUser


class EmailAndSecurityApiTestCase(TransactionTestCase):
    """
    Tests email sending behavior and security protections.
    """

    def setUp(self):
        cache.clear()
        self.client = APIClient()

        self.register_url = reverse("users-api:api-register")
        self.login_url = reverse("users-api:api-login")
        self.logout_url = reverse("users-api:api-logout")
        self.profile_url = reverse("users-api:api-profile")
        self.refresh_url = reverse("users-api:api-token-refresh")

        self.protected_url = self.profile_url

        self.user_data = {
            "email": "testuser@email.com",
            "password": "SecurePass123!",
            "user_name": "TestUser",
        }

    def test_register_sends_email(self):
        """
        Registering a user should send a confirmation email.
        """

        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertIn("Confirm your E-commerce Hub account", email.subject)
        self.assertIn(self.user_data["email"], email.to)

    def test_protected_endpoint_requires_jwt(self):
        """
        Protected endpoint should require authentication.
        """

        response = self.client.get(self.protected_url)

        self.assertEqual(response.status_code, 401)

    def test_profile_requires_confirmed_email_even_when_authenticated(self):
        """
        Authenticated but unconfirmed users must not access profile endpoint.
        """

        user = CustomUser.objects.create_user(
            email="unconfirmed@email.com",
            password="SecurePass123!",
            user_name="UnconfirmedUser",
            is_active=True,
            email_confirmed=False,
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 403)

    def test_login_with_jwt_access(self):
        """
        Confirmed active user should access protected endpoint with valid JWT.
        """

        CustomUser.objects.create_user(
            email="authuser@email.com",
            password="SecurePass123!",
            user_name="AuthUser",
            is_active=True,
            email_confirmed=True,
        )

        login_response = self.client.post(
            self.login_url,
            {
                "email": "authuser@email.com",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)

        access_token = login_response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get(self.protected_url)

        self.assertEqual(response.status_code, 200)

    def test_login_bruteforce_protection(self):
        """
        Simulate brute force login attempts and expect rate limiting.
        """

        CustomUser.objects.create_user(
            email="loginuser@email.com",
            password="CorrectPass123!",
            user_name="LoginUser",
            is_active=True,
            email_confirmed=True,
        )

        last_response = None

        for _ in range(10):
            last_response = self.client.post(
                self.login_url,
                {
                    "email": "loginuser@email.com",
                    "password": "WrongPassword",
                },
                format="json",
                REMOTE_ADDR="127.0.0.1",
            )

        self.assertEqual(last_response.status_code, 429)

    def test_login_rate_limit_per_ip(self):
        """
        Ensure rate limiting is applied per IP address.
        """

        CustomUser.objects.create_user(
            email="iplimit@email.com",
            password="CorrectPass123!",
            user_name="IpLimitUser",
            is_active=True,
            email_confirmed=True,
        )

        ip_address = "192.168.0.10"

        last_response = None

        for _ in range(10):
            last_response = self.client.post(
                self.login_url,
                {
                    "email": "iplimit@email.com",
                    "password": "WrongPassword",
                },
                format="json",
                REMOTE_ADDR=ip_address,
            )

        self.assertEqual(last_response.status_code, 429)

    def test_jwt_logout_blacklist(self):
        """
        Ensure logout blacklists refresh token.
        """

        user = CustomUser.objects.create_user(
            email="logoutuser@email.com",
            password="SecurePass123!",
            user_name="LogoutUser",
            is_active=True,
            email_confirmed=True,
        )

        login_response = self.client.post(
            self.login_url,
            {
                "email": "logoutuser@email.com",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)

        access = login_response.data["access"]
        refresh = login_response.data["refresh"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access}"
        )

        logout_response = self.client.post(
            self.logout_url,
            {"refresh": refresh},
            format="json",
        )

        self.assertIn(logout_response.status_code, [200, 205])

        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": refresh},
            format="json",
        )

        self.assertIn(refresh_response.status_code, [401, 403])

    def test_logout_requires_authenticated_active_user(self):
        """
        Logout endpoint must reject unauthenticated requests.
        """

        response = self.client.post(
            self.logout_url,
            {"refresh": "fake-token"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)