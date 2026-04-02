from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from ech.users.services.user_log_service import UserLogService


class UserLogServiceTestCase(SimpleTestCase):
    def setUp(self):
        self.user = MagicMock()
        self.user.id = 1
        self.user.user_email = "user@test.com"
        self.user.user_role = "customer_user"
        self.user.is_active = False
        self.user.email_confirmed = False

        self.performed_by = MagicMock()
        self.performed_by.id = 99

    @patch("ech.users.services.user_log_service.logger")
    def test_log_user_registered(self, mock_logger):
        UserLogService.log_user_registered(
            user=self.user,
            performed_by=self.performed_by,
        )

        mock_logger.info.assert_called_once_with(
            "User registered.",
            extra={
                "user_id": "1",
                "email": "user@test.com",
                "role": "customer_user",
                "is_active": False,
                "email_confirmed": False,
                "performed_by_id": 99,
            },
        )

    @patch("ech.users.services.user_log_service.logger")
    def test_log_user_email_confirmed(self, mock_logger):
        UserLogService.log_user_email_confirmed(
            user=self.user,
            performed_by=self.performed_by,
        )

        mock_logger.info.assert_called_once_with(
            "User email confirmed.",
            extra={
                "user_id": "1",
                "email": "user@test.com",
                "performed_by_id": 99,
            },
        )

    @patch("ech.users.services.user_log_service.logger")
    def test_log_user_profile_updated(self, mock_logger):
        UserLogService.log_user_profile_updated(
            user=self.user,
            changed_fields=["user_name", "user_phone"],
            performed_by=self.performed_by,
        )

        mock_logger.info.assert_called_once_with(
            "User profile updated.",
            extra={
                "user_id": "1",
                "email": "user@test.com",
                "changed_fields": ["user_name", "user_phone"],
                "performed_by_id": 99,
            },
        )

    @patch("ech.users.services.user_log_service.logger")
    def test_log_user_profile_updated_uses_empty_list_when_changed_fields_is_none(
        self,
        mock_logger,
    ):
        UserLogService.log_user_profile_updated(
            user=self.user,
            changed_fields=None,
            performed_by=self.performed_by,
        )

        mock_logger.info.assert_called_once_with(
            "User profile updated.",
            extra={
                "user_id": "1",
                "email": "user@test.com",
                "changed_fields": [],
                "performed_by_id": 99,
            },
        )

    @patch("ech.users.services.user_log_service.logger")
    def test_log_user_password_changed(self, mock_logger):
        UserLogService.log_user_password_changed(
            user=self.user,
            performed_by=self.performed_by,
        )

        mock_logger.info.assert_called_once_with(
            "User password changed.",
            extra={
                "user_id": "1",
                "email": "user@test.com",
                "performed_by_id": 99,
            },
        )

    @patch("ech.users.services.user_log_service.logger")
    def test_log_user_login_succeeded(self, mock_logger):
        UserLogService.log_user_login_succeeded(user=self.user)

        mock_logger.info.assert_called_once_with(
            "User login succeeded.",
            extra={
                "user_id": "1",
                "email": "user@test.com",
            },
        )

    @patch("ech.users.services.user_log_service.logger")
    def test_log_user_login_failed(self, mock_logger):
        UserLogService.log_user_login_failed(email="user@test.com")

        mock_logger.warning.assert_called_once_with(
            "User login failed.",
            extra={
                "email": "user@test.com",
            },
        )

    @patch("ech.users.services.user_log_service.logger")
    def test_log_user_registered_without_performed_by(self, mock_logger):
        UserLogService.log_user_registered(user=self.user)

        mock_logger.info.assert_called_once_with(
            "User registered.",
            extra={
                "user_id": "1",
                "email": "user@test.com",
                "role": "customer_user",
                "is_active": False,
                "email_confirmed": False,
                "performed_by_id": None,
            },
        )

    @patch("ech.users.services.user_log_service.logger")
    def test_log_user_email_confirmed_without_performed_by(self, mock_logger):
        UserLogService.log_user_email_confirmed(user=self.user)

        mock_logger.info.assert_called_once_with(
            "User email confirmed.",
            extra={
                "user_id": "1",
                "email": "user@test.com",
                "performed_by_id": None,
            },
        )

    @patch("ech.users.services.user_log_service.logger")
    def test_log_user_password_changed_without_performed_by(self, mock_logger):
        UserLogService.log_user_password_changed(user=self.user)

        mock_logger.info.assert_called_once_with(
            "User password changed.",
            extra={
                "user_id": "1",
                "email": "user@test.com",
                "performed_by_id": None,
            },
        )