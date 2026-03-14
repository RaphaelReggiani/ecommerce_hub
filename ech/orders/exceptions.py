from ech.orders.constants.messages import (
    MSG_EXCEPTIONS_ERROR_UNEXPECTED_ORDER ,
    MSG_EXCEPTIONS_ERROR_ORDER_NOT_FOUND,
    MSG_EXCEPTIONS_ERROR_NO_PERMISSION,
    MSG_EXCEPTIONS_ERROR_ITEM_PROVIDED,
    MSG_EXCEPTIONS_ERROR_INVALID_ADDRESS,
    MSG_EXCEPTIONS_ERROR_DUPLICATED_ORDER,
    MSG_EXCEPTIONS_ERROR_PRODUCT_NOT_AVAILABLE,
    MSG_EXCEPTIONS_ERROR_PRODUCT_IS_INACTIVE,
    MSG_EXCEPTIONS_ERROR_INSUFFICIENT_INVETORY,
    MSG_EXCEPTIONS_ERROR_INVALID_TRANSITION_STATUS,
    MSG_EXCEPTIONS_ERROR_ORDER_CANNOT_BE_CANCELLED,
    MSG_EXCEPTIONS_ERROR_ORDER_IS_ALREADY_CANCELLED,
    MSG_EXCEPTIONS_ERROR_ORDER_ALREADY_SHIPPED,
    MSG_EXCEPTIONS_ERROR_ORDER_ALREADY_DELIVERED,
    MSG_EXCEPTIONS_ERROR_INVALID_PAYMENT_STATUS,
    MSG_EXCEPTIONS_ERROR_INVALID_SHIPPING_STATUS,
)


class OrderError(Exception):
    """
    Base exception for the orders domain.
    """
    default_message = MSG_EXCEPTIONS_ERROR_UNEXPECTED_ORDER

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class OrderNotFoundError(OrderError):
    """
    Raised when an order cannot be found.
    """
    default_message = MSG_EXCEPTIONS_ERROR_ORDER_NOT_FOUND


class OrderPermissionDeniedError(OrderError):
    """
    Raised when a user does not have permission
    to access or manage an order.
    """
    default_message = MSG_EXCEPTIONS_ERROR_NO_PERMISSION


class EmptyOrderError(OrderError):
    """
    Raised when attempting to create an order without items.
    """
    default_message = MSG_EXCEPTIONS_ERROR_ITEM_PROVIDED


class InvalidOrderAddressError(OrderError):
    """
    Raised when the provided order address data is invalid.
    """
    default_message = MSG_EXCEPTIONS_ERROR_INVALID_ADDRESS


class DuplicateOrderError(OrderError):
    """
    Raised when an order duplication attempt is detected
    and idempotency rules are violated.
    """
    default_message = MSG_EXCEPTIONS_ERROR_DUPLICATED_ORDER


class ProductNotAvailableError(OrderError):
    """
    Raised when a product does not exist
    or is not available for ordering.
    """
    default_message = MSG_EXCEPTIONS_ERROR_PRODUCT_NOT_AVAILABLE


class InactiveProductError(OrderError):
    """
    Raised when a product exists but is inactive.
    """
    default_message = MSG_EXCEPTIONS_ERROR_PRODUCT_IS_INACTIVE


class InsufficientInventoryError(OrderError):
    """
    Raised when there is not enough stock
    to fulfill the requested quantity.
    """
    default_message = MSG_EXCEPTIONS_ERROR_INSUFFICIENT_INVETORY


class InvalidOrderStatusTransitionError(OrderError):
    """
    Raised when an order status transition is invalid.
    """
    default_message = MSG_EXCEPTIONS_ERROR_INVALID_TRANSITION_STATUS


class OrderCancellationNotAllowedError(OrderError):
    """
    Raised when an order cannot be cancelled.
    """
    default_message = MSG_EXCEPTIONS_ERROR_ORDER_CANNOT_BE_CANCELLED


class OrderAlreadyCancelledError(OrderError):
    """
    Raised when attempting to cancel an already cancelled order.
    """
    default_message = MSG_EXCEPTIONS_ERROR_ORDER_IS_ALREADY_CANCELLED


class OrderAlreadyShippedError(OrderError):
    """
    Raised when an operation is invalid because the order
    has already been shipped.
    """
    default_message = MSG_EXCEPTIONS_ERROR_ORDER_ALREADY_SHIPPED


class OrderAlreadyDeliveredError(OrderError):
    """
    Raised when an operation is invalid because the order
    has already been delivered.
    """
    default_message = MSG_EXCEPTIONS_ERROR_ORDER_ALREADY_DELIVERED


class InvalidPaymentStatusError(OrderError):
    """
    Raised when a payment status is invalid for the requested action.
    """
    default_message = MSG_EXCEPTIONS_ERROR_INVALID_PAYMENT_STATUS


class InvalidShippingStatusError(OrderError):
    """
    Raised when a shipping status is invalid for the requested action.
    """
    default_message = MSG_EXCEPTIONS_ERROR_INVALID_SHIPPING_STATUS

