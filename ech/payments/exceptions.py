from ech.payments.constants.messages import (
    MSG_EXCEPTIONS_ERROR_UNEXPECTED_PAYMENT,
    MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND,
    MSG_EXCEPTIONS_ERROR_PERMISSION_DENIED_TO_PERFORM_PAYMENT,
    MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_ALLOWED_FOR_ORDER,
    MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_PROCESSED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_PROCESSED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_PROCESSING_FAILED,
    MSG_EXCEPTIONS_ERROR_INVALID_PAYMENT_TRANSITION,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_CANCELLED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_CANCELLED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_REFUNDED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_REFUNDED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_IS_NOT_REFUNDABLE,
    MSG_EXCEPTIONS_ERROR_REFUND_AMOUNT_EXCEEDS_AVAILABLE_REFUNDABLE_BALANCE,
    MSG_EXCEPTIONS_ERROR_INVALID_REFUND_AMOUNT,
    MSG_EXCEPTIONS_ERROR_PAYMENT_TRANSACTION_NOT_FOUND,
    MSG_EXCEPTIONS_ERROR_PAYMENT_TRANSACTION_NOT_ALLOWED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_REFERENCE_ALREADY_EXISTS,
    MSG_EXCEPTIONS_ERROR_IDEMPOTENCY_KEY_ALREADY_BEEN_USED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_DATA_DOES_NOT_MATCH,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CUSTOMER_DOES_NOT_MATCH,
    MSG_EXCEPTIONS_ERROR_PAYMENT_AMOUNT_DOES_NOT_MATCH,
    MSG_EXCEPTIONS_ERROR_REFUND_PROCESSING_FAILED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_REFUND_NOT_FOUND,
    MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_PROCESSED,
    MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_CANCELLED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_CANCELLED_IN_ITS_STATE,
)

class PaymentError(Exception):
    """
    Base exception for all payment domain errors.
    """

    default_message = MSG_EXCEPTIONS_ERROR_UNEXPECTED_PAYMENT

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class PaymentNotFound(PaymentError):
    """
    Raised when the requested payment does not exist.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND


class PaymentPermissionDenied(PaymentError):
    """
    Raised when the user does not have permission
    to access or manage the payment resource.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PERMISSION_DENIED_TO_PERFORM_PAYMENT


class PaymentCreationNotAllowed(PaymentError):
    """
    Raised when a payment cannot be created
    for the given order or context.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_ALLOWED_FOR_ORDER


class PaymentAlreadyProcessed(PaymentError):
    """
    Raised when attempting to process a payment
    that has already been processed.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_PROCESSED


class PaymentProcessingNotAllowed(PaymentError):
    """
    Raised when the payment is in a state
    that does not allow processing.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_PROCESSED


class PaymentProcessingFailed(PaymentError):
    """
    Raised when the payment processing operation fails.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_PROCESSING_FAILED


class InvalidPaymentStatusTransition(PaymentError):
    """
    Raised when attempting an invalid payment status transition.
    """

    default_message = MSG_EXCEPTIONS_ERROR_INVALID_PAYMENT_TRANSITION


class PaymentCancellationNotAllowed(PaymentError):
    """
    Raised when attempting to cancel a payment
    that cannot be cancelled.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_CANCELLED


class PaymentAlreadyCancelled(PaymentError):
    """
    Raised when attempting to cancel
    an already cancelled payment.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_CANCELLED


class PaymentRefundNotAllowed(PaymentError):
    """
    Raised when attempting to refund a payment
    that is not eligible for refund.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_REFUNDED


class PaymentAlreadyRefunded(PaymentError):
    """
    Raised when attempting to refund
    an already fully refunded payment.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_REFUNDED


class PaymentNotRefundable(PaymentError):
    """
    Raised when the payment has no refundable balance
    or does not support refunds in its current state.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_IS_NOT_REFUNDABLE


class RefundAmountExceeded(PaymentError):
    """
    Raised when the requested refund amount
    exceeds the available refundable amount.
    """

    default_message = MSG_EXCEPTIONS_ERROR_REFUND_AMOUNT_EXCEEDS_AVAILABLE_REFUNDABLE_BALANCE


class InvalidRefundAmount(PaymentError):
    """
    Raised when the refund amount is invalid.
    """

    default_message = MSG_EXCEPTIONS_ERROR_INVALID_REFUND_AMOUNT


class PaymentTransactionNotFound(PaymentError):
    """
    Raised when the requested payment transaction does not exist.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_TRANSACTION_NOT_FOUND


class PaymentTransactionNotAllowed(PaymentError):
    """
    Raised when the requested transaction operation
    is not allowed for the payment.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_TRANSACTION_NOT_ALLOWED


class DuplicatePaymentReference(PaymentError):
    """
    Raised when a duplicate payment reference is detected.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_REFERENCE_ALREADY_EXISTS


class DuplicateIdempotencyKey(PaymentError):
    """
    Raised when a duplicated idempotency key is detected.
    """

    default_message = MSG_EXCEPTIONS_ERROR_IDEMPOTENCY_KEY_ALREADY_BEEN_USED


class PaymentOrderMismatch(PaymentError):
    """
    Raised when the payment data does not match
    the related order data.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_DATA_DOES_NOT_MATCH


class PaymentCustomerMismatch(PaymentError):
    """
    Raised when the payment customer does not match
    the related order customer.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_CUSTOMER_DOES_NOT_MATCH


class PaymentAmountMismatch(PaymentError):
    """
    Raised when the payment amount is inconsistent
    with the expected order total.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_AMOUNT_DOES_NOT_MATCH


class RefundProcessingFailed(PaymentError):
    """
    Raised when the refund processing operation fails.
    """

    default_message = MSG_EXCEPTIONS_ERROR_REFUND_PROCESSING_FAILED


class PaymentRefundNotFound(PaymentError):
    """
    Raised when the requested refund does not exist.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_REFUND_NOT_FOUND


class RefundAlreadyProcessed(PaymentError):
    """
    Raised when attempting to process an already processed refund.
    """

    default_message = MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_PROCESSED


class RefundAlreadyCancelled(PaymentError):
    """
    Raised when attempting to cancel an already cancelled refund.
    """

    default_message = MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_CANCELLED


class RefundProcessingNotAllowed(PaymentError):
    """
    Raised when a refund cannot be processed in its current state.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_PROCESSED


class RefundCancellationNotAllowed(PaymentError):
    """
    Raised when a refund cannot be cancelled in its current state.
    """

    default_message = MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_CANCELLED_IN_ITS_STATE