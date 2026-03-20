from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase

from ech.users.logs.security_events import (
    log_login_success,
    log_login_failed,
    log_user_registered,
    log_email_confirmed,
    log_password_changed,
    log_token_invalid,
    log_password_reset_requested,
)


class SecurityEventsTestCase(SimpleTestCase):
    def setUp(self):
        self.request = MagicMock()
        self.user = MagicMock()
        self.user.id = 1
        self.user.user_email = "user@test.com"

    @patch("ech.users.logs.security_events.get_request_id", return_value="req-123")
    @patch("ech.users.logs.security_events.get_user_agent", return_value="agent")
    @patch("ech.users.logs.security_events.get_client_ip", return_value="127.0.0.1")
    @patch("ech.users.logs.security_events.logger")
    def test_log_login_success(self, mock_logger, *_):
        """Ensure login_success logs correct event and metadata."""
        log_login_success(self.request, self.user)

        mock_logger.info.assert_called_once_with(
            "login_success",
            extra={
                "user_id": 1,
                "email": "user@test.com",
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )

    @patch("ech.users.logs.security_events.get_request_id", return_value="req-123")
    @patch("ech.users.logs.security_events.get_user_agent", return_value="agent")
    @patch("ech.users.logs.security_events.get_client_ip", return_value="127.0.0.1")
    @patch("ech.users.logs.security_events.logger")
    def test_log_login_failed(self, mock_logger, *_):
        """Ensure login_failed logs warning with correct metadata."""
        log_login_failed(self.request, "user@test.com")

        mock_logger.warning.assert_called_once_with(
            "login_failed",
            extra={
                "email": "user@test.com",
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )

    @patch("ech.users.logs.security_events.get_request_id", return_value="req-123")
    @patch("ech.users.logs.security_events.get_user_agent", return_value="agent")
    @patch("ech.users.logs.security_events.get_client_ip", return_value="127.0.0.1")
    @patch("ech.users.logs.security_events.logger")
    def test_log_user_registered(self, mock_logger, *_):
        """Ensure user_registered logs correct data."""
        log_user_registered(self.request, self.user)

        mock_logger.info.assert_called_once_with(
            "user_registered",
            extra={
                "user_id": 1,
                "email": "user@test.com",
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )

    @patch("ech.users.logs.security_events.get_request_id", return_value="req-123")
    @patch("ech.users.logs.security_events.get_client_ip", return_value="127.0.0.1")
    @patch("ech.users.logs.security_events.logger")
    def test_log_email_confirmed(self, mock_logger, *_):
        """Ensure email_confirmed logs correct data."""
        log_email_confirmed(self.request, self.user)

        mock_logger.info.assert_called_once_with(
            "email_confirmed",
            extra={
                "user_id": 1,
                "email": "user@test.com",
                "ip_address": "127.0.0.1",
                "request_id": "req-123",
            },
        )

    @patch("ech.users.logs.security_events.get_request_id", return_value="req-123")
    @patch("ech.users.logs.security_events.get_client_ip", return_value="127.0.0.1")
    @patch("ech.users.logs.security_events.logger")
    def test_log_password_changed(self, mock_logger, *_):
        """Ensure password_changed logs correct data."""
        log_password_changed(self.request, self.user)

        mock_logger.info.assert_called_once_with(
            "password_changed",
            extra={
                "user_id": 1,
                "ip_address": "127.0.0.1",
                "request_id": "req-123",
            },
        )

    @patch("ech.users.logs.security_events.get_request_id", return_value="req-123")
    @patch("ech.users.logs.security_events.get_user_agent", return_value="agent")
    @patch("ech.users.logs.security_events.get_client_ip", return_value="127.0.0.1")
    @patch("ech.users.logs.security_events.logger")
    def test_log_token_invalid(self, mock_logger, *_):
        """Ensure token_invalid logs warning with correct data."""
        log_token_invalid(self.request, "password_reset")

        mock_logger.warning.assert_called_once_with(
            "token_invalid",
            extra={
                "token_type": "password_reset",
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )

    @patch("ech.users.logs.security_events.get_request_id", return_value="req-123")
    @patch("ech.users.logs.security_events.get_user_agent", return_value="agent")
    @patch("ech.users.logs.security_events.get_client_ip", return_value="127.0.0.1")
    @patch("ech.users.logs.security_events.logger")
    def test_log_password_reset_requested(self, mock_logger, *_):
        """Ensure password_reset_requested logs correct data."""
        log_password_reset_requested(self.request, self.user)

        mock_logger.info.assert_called_once_with(
            "password_reset_requested",
            extra={
                "user_id": 1,
                "email": "user@test.com",
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )