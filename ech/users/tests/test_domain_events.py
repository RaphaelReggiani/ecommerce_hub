import uuid
from importlib import import_module
from unittest.mock import patch

from django.test import SimpleTestCase

from ech.users.apps import UsersConfig
from ech.users.domain_events.dispatcher import DomainEventDispatcher
from ech.users.domain_events.events import (
    BaseDomainEvent,
    UserEmailConfirmedEvent,
    UserLoginFailedEvent,
    UserLoginSucceededEvent,
    UserPasswordChangedEvent,
    UserPasswordResetRequestedEvent,
    UserRegisteredEvent,
    UserTokenInvalidEvent,
)
from ech.users.domain_events.handlers import (
    handle_user_email_confirmed,
    handle_user_login_failed,
    handle_user_login_succeeded,
    handle_user_password_changed,
    handle_user_password_reset_requested,
    handle_user_registered,
    handle_user_token_invalid,
)
from ech.users.domain_events.registry import EVENT_HANDLER_REGISTRY


class UsersAppConfigTestCase(SimpleTestCase):
    def test_ready_imports_domain_event_registry(self):
        """Import domain event registry when app config is ready."""
        config = UsersConfig("ech.users", import_module("ech.users"))

        with patch("ech.users.domain_events.registry.EVENT_HANDLER_REGISTRY", {}) as _:
            config.ready()


class BaseDomainEventTestCase(SimpleTestCase):
    def test_base_domain_event_to_dict_returns_event_payload_copy(self):
        """Return a copy of the event payload dictionary."""
        event = BaseDomainEvent()
        event.example_field = "example"
        event.numeric_field = 123

        payload = event.to_dict()

        self.assertEqual(
            payload,
            {
                "example_field": "example",
                "numeric_field": 123,
            },
        )
        self.assertIsNot(payload, event.__dict__)

    def test_base_domain_event_exposes_default_event_name(self):
        """Expose the default base event name."""
        self.assertEqual(BaseDomainEvent.event_name, "base_domain_event")


class UserRegisteredEventTestCase(SimpleTestCase):
    def test_user_registered_event_stores_expected_payload(self):
        """Store the expected payload for user registered event."""
        event = UserRegisteredEvent(
            user_id=1,
            email="user@test.com",
            role="customer_user",
            performed_by_id=10,
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        self.assertEqual(event.event_name, "user_registered")
        self.assertEqual(event.user_id, 1)
        self.assertEqual(event.email, "user@test.com")
        self.assertEqual(event.role, "customer_user")
        self.assertEqual(event.performed_by_id, 10)
        self.assertEqual(event.ip_address, "127.0.0.1")
        self.assertEqual(event.user_agent, "agent")
        self.assertEqual(event.request_id, "req-123")

    def test_user_registered_event_to_dict_serializes_payload(self):
        """Serialize user registered event payload correctly."""
        event = UserRegisteredEvent(
            user_id=1,
            email="user@test.com",
            role="customer_user",
            performed_by_id=None,
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        self.assertEqual(
            event.to_dict(),
            {
                "user_id": 1,
                "email": "user@test.com",
                "role": "customer_user",
                "performed_by_id": None,
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )


class UserEmailConfirmedEventTestCase(SimpleTestCase):
    def test_user_email_confirmed_event_stores_expected_payload(self):
        """Store the expected payload for user email confirmed event."""
        event = UserEmailConfirmedEvent(
            user_id=1,
            email="user@test.com",
            performed_by_id=20,
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        self.assertEqual(event.event_name, "user_email_confirmed")
        self.assertEqual(event.user_id, 1)
        self.assertEqual(event.email, "user@test.com")
        self.assertEqual(event.performed_by_id, 20)
        self.assertEqual(event.ip_address, "127.0.0.1")
        self.assertEqual(event.user_agent, "agent")
        self.assertEqual(event.request_id, "req-123")


class UserPasswordResetRequestedEventTestCase(SimpleTestCase):
    def test_user_password_reset_requested_event_stores_expected_payload(self):
        """Store the expected payload for password reset requested event."""
        event = UserPasswordResetRequestedEvent(
            user_id=1,
            email="user@test.com",
            performed_by_id=None,
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        self.assertEqual(event.event_name, "user_password_reset_requested")
        self.assertEqual(event.user_id, 1)
        self.assertEqual(event.email, "user@test.com")
        self.assertIsNone(event.performed_by_id)
        self.assertEqual(event.ip_address, "127.0.0.1")
        self.assertEqual(event.user_agent, "agent")
        self.assertEqual(event.request_id, "req-123")


class UserPasswordChangedEventTestCase(SimpleTestCase):
    def test_user_password_changed_event_stores_expected_payload(self):
        """Store the expected payload for password changed event."""
        event = UserPasswordChangedEvent(
            user_id=1,
            performed_by_id=30,
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        self.assertEqual(event.event_name, "user_password_changed")
        self.assertEqual(event.user_id, 1)
        self.assertEqual(event.performed_by_id, 30)
        self.assertEqual(event.ip_address, "127.0.0.1")
        self.assertEqual(event.user_agent, "agent")
        self.assertEqual(event.request_id, "req-123")


class UserLoginSucceededEventTestCase(SimpleTestCase):
    def test_user_login_succeeded_event_stores_expected_payload(self):
        """Store the expected payload for successful login event."""
        event = UserLoginSucceededEvent(
            user_id=1,
            email="user@test.com",
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        self.assertEqual(event.event_name, "user_login_succeeded")
        self.assertEqual(event.user_id, 1)
        self.assertEqual(event.email, "user@test.com")
        self.assertEqual(event.ip_address, "127.0.0.1")
        self.assertEqual(event.user_agent, "agent")
        self.assertEqual(event.request_id, "req-123")


class UserLoginFailedEventTestCase(SimpleTestCase):
    def test_user_login_failed_event_stores_expected_payload(self):
        """Store the expected payload for failed login event."""
        event = UserLoginFailedEvent(
            email="user@test.com",
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        self.assertEqual(event.event_name, "user_login_failed")
        self.assertEqual(event.email, "user@test.com")
        self.assertEqual(event.ip_address, "127.0.0.1")
        self.assertEqual(event.user_agent, "agent")
        self.assertEqual(event.request_id, "req-123")


class UserTokenInvalidEventTestCase(SimpleTestCase):
    def test_user_token_invalid_event_stores_expected_payload(self):
        """Store the expected payload for invalid token event."""
        event = UserTokenInvalidEvent(
            token_type="password_reset",
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        self.assertEqual(event.event_name, "user_token_invalid")
        self.assertEqual(event.token_type, "password_reset")
        self.assertEqual(event.ip_address, "127.0.0.1")
        self.assertEqual(event.user_agent, "agent")
        self.assertEqual(event.request_id, "req-123")


class DomainEventRegistryTestCase(SimpleTestCase):
    def test_event_handler_registry_contains_user_registered_event_mapping(self):
        """Register the user registered handler for user registered event."""
        self.assertIn(UserRegisteredEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[UserRegisteredEvent],
            [handle_user_registered],
        )

    def test_event_handler_registry_contains_user_email_confirmed_event_mapping(self):
        """Register the email confirmed handler for email confirmed event."""
        self.assertIn(UserEmailConfirmedEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[UserEmailConfirmedEvent],
            [handle_user_email_confirmed],
        )

    def test_event_handler_registry_contains_password_reset_requested_event_mapping(
        self,
    ):
        """Register the password reset requested handler."""
        self.assertIn(UserPasswordResetRequestedEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[UserPasswordResetRequestedEvent],
            [handle_user_password_reset_requested],
        )

    def test_event_handler_registry_contains_password_changed_event_mapping(self):
        """Register the password changed handler."""
        self.assertIn(UserPasswordChangedEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[UserPasswordChangedEvent],
            [handle_user_password_changed],
        )

    def test_event_handler_registry_contains_login_succeeded_event_mapping(self):
        """Register the login succeeded handler."""
        self.assertIn(UserLoginSucceededEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[UserLoginSucceededEvent],
            [handle_user_login_succeeded],
        )

    def test_event_handler_registry_contains_login_failed_event_mapping(self):
        """Register the login failed handler."""
        self.assertIn(UserLoginFailedEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[UserLoginFailedEvent],
            [handle_user_login_failed],
        )

    def test_event_handler_registry_contains_token_invalid_event_mapping(self):
        """Register the token invalid handler."""
        self.assertIn(UserTokenInvalidEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[UserTokenInvalidEvent],
            [handle_user_token_invalid],
        )


class DomainEventDispatcherTestCase(SimpleTestCase):
    def test_dispatch_calls_registered_handler_for_user_registered_event(self):
        """Dispatch user registered event to its registered handler."""
        event = UserRegisteredEvent(
            user_id=1,
            email="user@test.com",
            role="customer_user",
            performed_by_id=2,
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        captured_events = []

        def handler(event_obj):
            captured_events.append(event_obj)

        with patch(
            "ech.users.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {UserRegisteredEvent: [handler]},
        ):
            DomainEventDispatcher.dispatch(event)

        self.assertEqual(captured_events, [event])

    def test_dispatch_calls_multiple_registered_handlers(self):
        """Dispatch event to all handlers registered for its class."""
        event = UserTokenInvalidEvent(
            token_type="password_reset",
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        captured_calls = []

        def handler_one(event_obj):
            captured_calls.append(("handler_one", event_obj))

        def handler_two(event_obj):
            captured_calls.append(("handler_two", event_obj))

        with patch(
            "ech.users.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {
                UserTokenInvalidEvent: [
                    handler_one,
                    handler_two,
                ]
            },
        ):
            DomainEventDispatcher.dispatch(event)

        self.assertEqual(
            captured_calls,
            [
                ("handler_one", event),
                ("handler_two", event),
            ],
        )

    def test_dispatch_does_nothing_when_event_has_no_registered_handlers(self):
        """Do nothing when no handlers are registered for an event class."""

        class UnregisteredEvent(BaseDomainEvent):
            event_name = "unregistered_event"

        event = UnregisteredEvent()

        with patch(
            "ech.users.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {},
        ):
            DomainEventDispatcher.dispatch(event)


class DomainEventHandlersTestCase(SimpleTestCase):
    @patch("ech.users.domain_events.handlers.logger.info")
    def test_handle_user_registered_logs_expected_payload(self, logger_info_mock):
        """Log the expected payload for user registered handler."""
        event = UserRegisteredEvent(
            user_id=1,
            email="user@test.com",
            role="customer_user",
            performed_by_id=20,
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        handle_user_registered(event)

        logger_info_mock.assert_called_once_with(
            "Handled user registered domain event.",
            extra={
                "event_name": "user_registered",
                "user_id": "1",
                "email": "user@test.com",
                "role": "customer_user",
                "performed_by_id": 20,
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )

    @patch("ech.users.domain_events.handlers.logger.info")
    def test_handle_user_email_confirmed_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log the expected payload for user email confirmed handler."""
        event = UserEmailConfirmedEvent(
            user_id=1,
            email="user@test.com",
            performed_by_id=20,
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        handle_user_email_confirmed(event)

        logger_info_mock.assert_called_once_with(
            "Handled user email confirmed domain event.",
            extra={
                "event_name": "user_email_confirmed",
                "user_id": "1",
                "email": "user@test.com",
                "performed_by_id": 20,
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )

    @patch("ech.users.domain_events.handlers.logger.info")
    def test_handle_user_password_reset_requested_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log the expected payload for password reset requested handler."""
        event = UserPasswordResetRequestedEvent(
            user_id=1,
            email="user@test.com",
            performed_by_id=None,
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        handle_user_password_reset_requested(event)

        logger_info_mock.assert_called_once_with(
            "Handled user password reset requested domain event.",
            extra={
                "event_name": "user_password_reset_requested",
                "user_id": "1",
                "email": "user@test.com",
                "performed_by_id": None,
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )

    @patch("ech.users.domain_events.handlers.logger.info")
    def test_handle_user_password_changed_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log the expected payload for password changed handler."""
        event = UserPasswordChangedEvent(
            user_id=1,
            performed_by_id=30,
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        handle_user_password_changed(event)

        logger_info_mock.assert_called_once_with(
            "Handled user password changed domain event.",
            extra={
                "event_name": "user_password_changed",
                "user_id": "1",
                "performed_by_id": 30,
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )

    @patch("ech.users.domain_events.handlers.logger.info")
    def test_handle_user_login_succeeded_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log the expected payload for successful login handler."""
        event = UserLoginSucceededEvent(
            user_id=1,
            email="user@test.com",
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        handle_user_login_succeeded(event)

        logger_info_mock.assert_called_once_with(
            "Handled user login succeeded domain event.",
            extra={
                "event_name": "user_login_succeeded",
                "user_id": "1",
                "email": "user@test.com",
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )

    @patch("ech.users.domain_events.handlers.logger.warning")
    def test_handle_user_login_failed_logs_expected_payload(
        self,
        logger_warning_mock,
    ):
        """Log the expected payload for failed login handler."""
        event = UserLoginFailedEvent(
            email="user@test.com",
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        handle_user_login_failed(event)

        logger_warning_mock.assert_called_once_with(
            "Handled user login failed domain event.",
            extra={
                "event_name": "user_login_failed",
                "email": "user@test.com",
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )

    @patch("ech.users.domain_events.handlers.logger.warning")
    def test_handle_user_token_invalid_logs_expected_payload(
        self,
        logger_warning_mock,
    ):
        """Log the expected payload for invalid token handler."""
        event = UserTokenInvalidEvent(
            token_type="password_reset",
            ip_address="127.0.0.1",
            user_agent="agent",
            request_id="req-123",
        )

        handle_user_token_invalid(event)

        logger_warning_mock.assert_called_once_with(
            "Handled user invalid token domain event.",
            extra={
                "event_name": "user_token_invalid",
                "token_type": "password_reset",
                "ip_address": "127.0.0.1",
                "user_agent": "agent",
                "request_id": "req-123",
            },
        )