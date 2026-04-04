from django.test import SimpleTestCase

from ech.notifications.constants.messages import (
    MSG_NOTIFICATION_NOT_FOUND,
    MSG_NOTIFICATION_ALREADY_EXISTS,
    MSG_NOTIFICATION_MANAGEMENT_ACCESS_DENIED,
    MSG_INVALID_NOTIFICATION_OPERATION,
    MSG_INVALID_NOTIFICATION_STATE,
    MSG_NOTIFICATION_ALREADY_READ,
    MSG_NOTIFICATION_ALREADY_ARCHIVED,
    MSG_NOTIFICATION_ALREADY_CANCELLED,
    MSG_NOTIFICATION_DISPATCH_FAILED,
)

from ech.notifications.exceptions import (
    NotificationException,
    NotificationNotFoundException,
    NotificationAccessDeniedException,
    NotificationAlreadyExistsException,
    InvalidNotificationOperationException,
    InvalidNotificationStateTransitionException,
    NotificationAlreadyReadException,
    NotificationAlreadyArchivedException,
    NotificationAlreadyCancelledException,
    NotificationDispatchFailedException,
)


class NotificationExceptionTestCase(SimpleTestCase):
    def test_notification_exception_inherits_from_exception(self):
        """Inherit the base notification exception from Python Exception."""
        self.assertTrue(issubclass(NotificationException, Exception))

    def test_notification_exception_accepts_custom_message(self):
        """Store a custom message in the base notification exception."""
        exception = NotificationException("Custom notification error")

        self.assertEqual(str(exception), "Custom notification error")


class NotificationNotFoundExceptionTestCase(SimpleTestCase):
    def test_notification_not_found_exception_inherits_from_notification_exception(self):
        """Inherit notification not found exception from NotificationException."""
        self.assertTrue(
            issubclass(NotificationNotFoundException, NotificationException)
        )

    def test_notification_not_found_exception_uses_default_message(self):
        """Use the default notification not found message."""
        exception = NotificationNotFoundException()

        self.assertEqual(str(exception), MSG_NOTIFICATION_NOT_FOUND)

    def test_notification_not_found_exception_accepts_custom_message(self):
        """Allow a custom message for notification not found exception."""
        exception = NotificationNotFoundException("Custom not found message")

        self.assertEqual(str(exception), "Custom not found message")


class NotificationAccessDeniedExceptionTestCase(SimpleTestCase):
    def test_notification_access_denied_exception_inherits_from_notification_exception(self):
        """Inherit notification access denied exception from NotificationException."""
        self.assertTrue(
            issubclass(NotificationAccessDeniedException, NotificationException)
        )

    def test_notification_access_denied_exception_uses_default_message(self):
        """Use the default notification access denied message."""
        exception = NotificationAccessDeniedException()

        self.assertEqual(str(exception), MSG_NOTIFICATION_MANAGEMENT_ACCESS_DENIED)

    def test_notification_access_denied_exception_accepts_custom_message(self):
        """Allow a custom message for notification access denied exception."""
        exception = NotificationAccessDeniedException(
            "Custom access denied message"
        )

        self.assertEqual(str(exception), "Custom access denied message")


class NotificationAlreadyExistsExceptionTestCase(SimpleTestCase):
    def test_notification_already_exists_exception_inherits_from_notification_exception(self):
        """Inherit notification already exists exception from NotificationException."""
        self.assertTrue(
            issubclass(NotificationAlreadyExistsException, NotificationException)
        )

    def test_notification_already_exists_exception_uses_default_message(self):
        """Use the default notification already exists message."""
        exception = NotificationAlreadyExistsException()

        self.assertEqual(str(exception), MSG_NOTIFICATION_ALREADY_EXISTS)

    def test_notification_already_exists_exception_accepts_custom_message(self):
        """Allow a custom message for notification already exists exception."""
        exception = NotificationAlreadyExistsException(
            "Custom already exists message"
        )

        self.assertEqual(str(exception), "Custom already exists message")


class InvalidNotificationOperationExceptionTestCase(SimpleTestCase):
    def test_invalid_notification_operation_exception_inherits_from_notification_exception(self):
        """Inherit invalid notification operation exception from NotificationException."""
        self.assertTrue(
            issubclass(InvalidNotificationOperationException, NotificationException)
        )

    def test_invalid_notification_operation_exception_uses_default_message(self):
        """Use the default invalid notification operation message."""
        exception = InvalidNotificationOperationException()

        self.assertEqual(str(exception), MSG_INVALID_NOTIFICATION_OPERATION)

    def test_invalid_notification_operation_exception_accepts_custom_message(self):
        """Allow a custom message for invalid notification operation exception."""
        exception = InvalidNotificationOperationException(
            "Custom invalid operation message"
        )

        self.assertEqual(str(exception), "Custom invalid operation message")


class InvalidNotificationStateTransitionExceptionTestCase(SimpleTestCase):
    def test_invalid_notification_state_transition_exception_inherits_from_notification_exception(self):
        """Inherit invalid notification state transition exception from NotificationException."""
        self.assertTrue(
            issubclass(
                InvalidNotificationStateTransitionException,
                NotificationException,
            )
        )

    def test_invalid_notification_state_transition_exception_uses_default_message(self):
        """Use the default invalid notification state transition message."""
        exception = InvalidNotificationStateTransitionException()

        self.assertEqual(str(exception), MSG_INVALID_NOTIFICATION_STATE)

    def test_invalid_notification_state_transition_exception_accepts_custom_message(self):
        """Allow a custom message for invalid notification state transition exception."""
        exception = InvalidNotificationStateTransitionException(
            "Custom invalid state transition message"
        )

        self.assertEqual(str(exception), "Custom invalid state transition message")


class NotificationAlreadyReadExceptionTestCase(SimpleTestCase):
    def test_notification_already_read_exception_inherits_from_notification_exception(self):
        """Inherit notification already read exception from NotificationException."""
        self.assertTrue(
            issubclass(NotificationAlreadyReadException, NotificationException)
        )

    def test_notification_already_read_exception_uses_default_message(self):
        """Use the default notification already read message."""
        exception = NotificationAlreadyReadException()

        self.assertEqual(str(exception), MSG_NOTIFICATION_ALREADY_READ)

    def test_notification_already_read_exception_accepts_custom_message(self):
        """Allow a custom message for notification already read exception."""
        exception = NotificationAlreadyReadException(
            "Custom already read message"
        )

        self.assertEqual(str(exception), "Custom already read message")


class NotificationAlreadyArchivedExceptionTestCase(SimpleTestCase):
    def test_notification_already_archived_exception_inherits_from_notification_exception(self):
        """Inherit notification already archived exception from NotificationException."""
        self.assertTrue(
            issubclass(NotificationAlreadyArchivedException, NotificationException)
        )

    def test_notification_already_archived_exception_uses_default_message(self):
        """Use the default notification already archived message."""
        exception = NotificationAlreadyArchivedException()

        self.assertEqual(str(exception), MSG_NOTIFICATION_ALREADY_ARCHIVED)

    def test_notification_already_archived_exception_accepts_custom_message(self):
        """Allow a custom message for notification already archived exception."""
        exception = NotificationAlreadyArchivedException(
            "Custom already archived message"
        )

        self.assertEqual(str(exception), "Custom already archived message")


class NotificationAlreadyCancelledExceptionTestCase(SimpleTestCase):
    def test_notification_already_cancelled_exception_inherits_from_notification_exception(self):
        """Inherit notification already cancelled exception from NotificationException."""
        self.assertTrue(
            issubclass(NotificationAlreadyCancelledException, NotificationException)
        )

    def test_notification_already_cancelled_exception_uses_default_message(self):
        """Use the default notification already cancelled message."""
        exception = NotificationAlreadyCancelledException()

        self.assertEqual(str(exception), MSG_NOTIFICATION_ALREADY_CANCELLED)

    def test_notification_already_cancelled_exception_accepts_custom_message(self):
        """Allow a custom message for notification already cancelled exception."""
        exception = NotificationAlreadyCancelledException(
            "Custom already cancelled message"
        )

        self.assertEqual(str(exception), "Custom already cancelled message")


class NotificationDispatchFailedExceptionTestCase(SimpleTestCase):
    def test_notification_dispatch_failed_exception_inherits_from_notification_exception(self):
        """Inherit notification dispatch failed exception from NotificationException."""
        self.assertTrue(
            issubclass(NotificationDispatchFailedException, NotificationException)
        )

    def test_notification_dispatch_failed_exception_uses_default_message(self):
        """Use the default notification dispatch failed message."""
        exception = NotificationDispatchFailedException()

        self.assertEqual(str(exception), MSG_NOTIFICATION_DISPATCH_FAILED)

    def test_notification_dispatch_failed_exception_accepts_custom_message(self):
        """Allow a custom message for notification dispatch failed exception."""
        exception = NotificationDispatchFailedException(
            "Custom dispatch failed message"
        )

        self.assertEqual(str(exception), "Custom dispatch failed message")