from ech.shipping.constants.messages import (
    SHIPMENT_NOT_FOUND,
    SHIPMENT_ALREADY_EXISTS,
    SHIPMENT_ACCESS_DENIED,
    SHIPMENT_UPDATE_NOT_ALLOWED,
    INVALID_SHIPMENT_STATUS_TRANSITION,
    SHIPMENT_ALREADY_DELIVERED,
    SHIPMENT_ALREADY_CANCELLED,
    SHIPMENT_CANCELLATION_NOT_ALLOWED,
    INVALID_SHIPPING_ADDRESS,
    TRACKING_CODE_REQUIRED,
    INVALID_TRACKING_EVENT,
    IDEMPOTENCY_KEY_CONFLICT,
)


class ShippingException(Exception):
    """
    Base exception for the shipping domain.
    """
    pass


class ShipmentNotFoundException(ShippingException):
    """
    Raised when a shipment cannot be found.
    """

    def __init__(self, message=SHIPMENT_NOT_FOUND):
        super().__init__(message)


class ShipmentAccessDeniedException(ShippingException):
    """
    Raised when a user attempts to access a shipment without permission.
    """

    def __init__(self, message=SHIPMENT_ACCESS_DENIED):
        super().__init__(message)


class ShipmentAlreadyExistsException(ShippingException):
    """
    Raised when attempting to create a shipment that already exists.
    """

    def __init__(self, message=SHIPMENT_ALREADY_EXISTS):
        super().__init__(message)


class InvalidShippingAddressException(ShippingException):
    """
    Raised when the provided shipping address is invalid.
    """

    def __init__(self, message=INVALID_SHIPPING_ADDRESS):
        super().__init__(message)


class ShipmentUpdateNotAllowedException(ShippingException):
    """
    Raised when shipment update is not allowed due to status restrictions.
    """

    def __init__(self, message=SHIPMENT_UPDATE_NOT_ALLOWED):
        super().__init__(message)


class InvalidShipmentStatusTransitionException(ShippingException):
    """
    Raised when attempting an invalid shipment status transition.
    """

    def __init__(self, message=INVALID_SHIPMENT_STATUS_TRANSITION):
        super().__init__(message)


class ShipmentAlreadyDeliveredException(ShippingException):
    """
    Raised when an operation is attempted on a delivered shipment.
    """

    def __init__(self, message=SHIPMENT_ALREADY_DELIVERED):
        super().__init__(message)


class ShipmentAlreadyCancelledException(ShippingException):
    """
    Raised when an operation is attempted on a cancelled shipment.
    """

    def __init__(self, message=SHIPMENT_ALREADY_CANCELLED):
        super().__init__(message)


class ShipmentCancellationNotAllowedException(ShippingException):
    """
    Raised when shipment cancellation is not allowed.
    """

    def __init__(self, message=SHIPMENT_CANCELLATION_NOT_ALLOWED):
        super().__init__(message)


class TrackingCodeRequiredException(ShippingException):
    """
    Raised when a tracking code is required but missing.
    """

    def __init__(self, message=TRACKING_CODE_REQUIRED):
        super().__init__(message)


class InvalidTrackingEventException(ShippingException):
    """
    Raised when an invalid tracking update event is provided.
    """

    def __init__(self, message=INVALID_TRACKING_EVENT):
        super().__init__(message)


class IdempotencyConflictException(ShippingException):
    """
    Raised when an idempotency key is reused with a different payload.
    """

    def __init__(self, message=IDEMPOTENCY_KEY_CONFLICT):
        super().__init__(message)