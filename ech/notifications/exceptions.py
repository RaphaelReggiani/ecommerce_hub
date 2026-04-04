from ech.notifications.constants.messages import (
    MSG_NOTIFICATION_NOT_FOUND,
    MSG_NOTIFICATION_CREATION_FAILED,
    MSG_NOTIFICATION_DUPLICATE_IDEMPOTENCY_KEY,
    MSG_NOTIFICATION_MANAGEMENT_ACCESS_DENIED,
    MSG_NOTIFICATION_ALREADY_READ,
    MSG_NOTIFICATION_ALREADY_ARCHIVED,
    MSG_NOTIFICATION_ALREADY_CANCELLED,
    MSG_NOTIFICATION_ALREADY_PROCESSED,
    MSG_INVALID_NOTIFICATION_STATE,
    MSG_INVALID_NOTIFICATION_OPERATION,
    MSG_NOTIFICATION_DELIVERY_FAILED,
    MSG_NOTIFICATION_DELIVERY_CHANNEL_NOT_SUPPORTED,
    MSG_NOTIFICATION_PROVIDER_FAILURE,
    MSG_NOTIFICATION_DISPATCH_FAILED,
    MSG_NOTIFICATION_ALREADY_EXISTS,
)


class NotificationException(Exception):
    """
    Base exception for the notifications domain.
    """
    pass


class NotificationNotFoundException(NotificationException):
    """
    Raised when a notification cannot be found.
    """

    def __init__(self, message=MSG_NOTIFICATION_NOT_FOUND):
        super().__init__(message)


class NotificationCreationException(NotificationException):
    """
    Raised when a notification cannot be created.
    """

    def __init__(self, message=MSG_NOTIFICATION_CREATION_FAILED):
        super().__init__(message)


class NotificationAlreadyExistsException(NotificationException):
    """
    Raised when attempting to create a notification
    that already exists in a conflicting way.
    """

    def __init__(self, message=MSG_NOTIFICATION_ALREADY_EXISTS):
        super().__init__(message)


class NotificationAccessDeniedException(NotificationException):
    """
    Raised when a user attempts to access or manage
    a notification without the required permissions.
    """

    def __init__(self, message=MSG_NOTIFICATION_MANAGEMENT_ACCESS_DENIED):
        super().__init__(message)


class NotificationAlreadyReadException(NotificationException):
    """
    Raised when attempting to mark a notification
    as read when it is already read.
    """

    def __init__(self, message=MSG_NOTIFICATION_ALREADY_READ):
        super().__init__(message)


class NotificationAlreadyArchivedException(NotificationException):
    """
    Raised when attempting to archive a notification
    that is already archived.
    """

    def __init__(self, message=MSG_NOTIFICATION_ALREADY_ARCHIVED):
        super().__init__(message)


class NotificationAlreadyCancelledException(NotificationException):
    """
    Raised when attempting to operate on a notification
    that has already been cancelled.
    """

    def __init__(self, message=MSG_NOTIFICATION_ALREADY_CANCELLED):
        super().__init__(message)


class NotificationAlreadyProcessedException(NotificationException):
    """
    Raised when attempting to modify a notification
    that has already been processed.
    """

    def __init__(self, message=MSG_NOTIFICATION_ALREADY_PROCESSED):
        super().__init__(message)


class InvalidNotificationStateTransitionException(NotificationException):
    """
    Raised when attempting an invalid notification
    status transition.
    """

    def __init__(self, message=MSG_INVALID_NOTIFICATION_STATE):
        super().__init__(message)


class InvalidNotificationOperationException(NotificationException):
    """
    Raised when an invalid notification operation
    is attempted.
    """

    def __init__(self, message=MSG_INVALID_NOTIFICATION_OPERATION):
        super().__init__(message)


class NotificationDispatchFailedException(NotificationException):
    """
    Raised when notification dispatch fails.
    """

    def __init__(self, message=MSG_NOTIFICATION_DISPATCH_FAILED):
        super().__init__(message)


class NotificationDeliveryFailedException(NotificationException):
    """
    Raised when notification delivery fails.
    """

    def __init__(self, message=MSG_NOTIFICATION_DELIVERY_FAILED):
        super().__init__(message)


class NotificationDeliveryChannelNotSupportedException(NotificationException):
    """
    Raised when a delivery channel is not supported.
    """

    def __init__(self, message=MSG_NOTIFICATION_DELIVERY_CHANNEL_NOT_SUPPORTED):
        super().__init__(message)


class NotificationProviderException(NotificationException):
    """
    Raised when a notification provider returns an error.
    """

    def __init__(self, message=MSG_NOTIFICATION_PROVIDER_FAILURE):
        super().__init__(message)


class NotificationIdempotencyConflictException(NotificationException):
    """
    Raised when an idempotency key is reused with a different payload.
    """

    def __init__(self, message=MSG_NOTIFICATION_DUPLICATE_IDEMPOTENCY_KEY):
        super().__init__(message)