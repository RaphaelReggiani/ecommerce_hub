from django.test import SimpleTestCase

from ech.payments.constants.messages import (
    MSG_EXCEPTIONS_ERROR_IDEMPOTENCY_KEY_ALREADY_BEEN_USED,
    MSG_EXCEPTIONS_ERROR_INVALID_PAYMENT_TRANSITION,
    MSG_EXCEPTIONS_ERROR_INVALID_REFUND_AMOUNT,
    MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_CANCELLED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_PROCESSED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_REFUNDED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_AMOUNT_DOES_NOT_MATCH,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_CANCELLED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_CANCELLED_IN_ITS_STATE,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_PROCESSED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_REFUNDED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CUSTOMER_DOES_NOT_MATCH,
    MSG_EXCEPTIONS_ERROR_PAYMENT_DATA_DOES_NOT_MATCH,
    MSG_EXCEPTIONS_ERROR_PAYMENT_IS_NOT_REFUNDABLE,
    MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_ALLOWED_FOR_ORDER,
    MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND,
    MSG_EXCEPTIONS_ERROR_PAYMENT_PROCESSING_FAILED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_REFUND_NOT_FOUND,
    MSG_EXCEPTIONS_ERROR_PAYMENT_REFERENCE_ALREADY_EXISTS,
    MSG_EXCEPTIONS_ERROR_PAYMENT_TRANSACTION_NOT_ALLOWED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_TRANSACTION_NOT_FOUND,
    MSG_EXCEPTIONS_ERROR_PERMISSION_DENIED_TO_PERFORM_PAYMENT,
    MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_CANCELLED,
    MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_PROCESSED,
    MSG_EXCEPTIONS_ERROR_REFUND_AMOUNT_EXCEEDS_AVAILABLE_REFUNDABLE_BALANCE,
    MSG_EXCEPTIONS_ERROR_REFUND_PROCESSING_FAILED,
    MSG_EXCEPTIONS_ERROR_UNEXPECTED_PAYMENT,
)
from ech.payments.exceptions import (
    DuplicateIdempotencyKey,
    DuplicatePaymentReference,
    InvalidPaymentStatusTransition,
    InvalidRefundAmount,
    PaymentAlreadyCancelled,
    PaymentAlreadyProcessed,
    PaymentAlreadyRefunded,
    PaymentAmountMismatch,
    PaymentCancellationNotAllowed,
    PaymentCreationNotAllowed,
    PaymentCustomerMismatch,
    PaymentError,
    PaymentNotFound,
    PaymentNotRefundable,
    PaymentOrderMismatch,
    PaymentPermissionDenied,
    PaymentProcessingFailed,
    PaymentProcessingNotAllowed,
    PaymentRefundNotAllowed,
    PaymentRefundNotFound,
    PaymentTransactionNotAllowed,
    PaymentTransactionNotFound,
    RefundAlreadyCancelled,
    RefundAlreadyProcessed,
    RefundAmountExceeded,
    RefundCancellationNotAllowed,
    RefundProcessingFailed,
    RefundProcessingNotAllowed,
)


class PaymentExceptionsTestCase(SimpleTestCase):
    def test_payment_error_uses_default_message(self):
        """Ensure PaymentError uses its default message when none is provided."""
        exception = PaymentError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_UNEXPECTED_PAYMENT)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_UNEXPECTED_PAYMENT)

    def test_payment_error_accepts_custom_message(self):
        """Ensure PaymentError accepts and exposes a custom message."""
        exception = PaymentError("Custom payment error.")

        self.assertEqual(exception.message, "Custom payment error.")
        self.assertEqual(str(exception), "Custom payment error.")

    def test_payment_not_found_default_message(self):
        """Ensure PaymentNotFound uses the expected default message."""
        exception = PaymentNotFound()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND)

    def test_payment_permission_denied_default_message(self):
        """Ensure PaymentPermissionDenied uses the expected default message."""
        exception = PaymentPermissionDenied()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PERMISSION_DENIED_TO_PERFORM_PAYMENT,
        )

    def test_payment_creation_not_allowed_default_message(self):
        """Ensure PaymentCreationNotAllowed uses the expected default message."""
        exception = PaymentCreationNotAllowed()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_ALLOWED_FOR_ORDER,
        )

    def test_payment_already_processed_default_message(self):
        """Ensure PaymentAlreadyProcessed uses the expected default message."""
        exception = PaymentAlreadyProcessed()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_PROCESSED,
        )

    def test_payment_processing_not_allowed_default_message(self):
        """Ensure PaymentProcessingNotAllowed uses the expected default message."""
        exception = PaymentProcessingNotAllowed()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_PROCESSED,
        )

    def test_payment_processing_failed_default_message(self):
        """Ensure PaymentProcessingFailed uses the expected default message."""
        exception = PaymentProcessingFailed()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_PROCESSING_FAILED,
        )

    def test_invalid_payment_status_transition_default_message(self):
        """Ensure InvalidPaymentStatusTransition uses the expected default message."""
        exception = InvalidPaymentStatusTransition()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_INVALID_PAYMENT_TRANSITION,
        )

    def test_payment_cancellation_not_allowed_default_message(self):
        """Ensure PaymentCancellationNotAllowed uses the expected default message."""
        exception = PaymentCancellationNotAllowed()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_CANCELLED,
        )

    def test_payment_already_cancelled_default_message(self):
        """Ensure PaymentAlreadyCancelled uses the expected default message."""
        exception = PaymentAlreadyCancelled()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_CANCELLED,
        )

    def test_payment_refund_not_allowed_default_message(self):
        """Ensure PaymentRefundNotAllowed uses the expected default message."""
        exception = PaymentRefundNotAllowed()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_REFUNDED,
        )

    def test_payment_already_refunded_default_message(self):
        """Ensure PaymentAlreadyRefunded uses the expected default message."""
        exception = PaymentAlreadyRefunded()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_REFUNDED,
        )

    def test_payment_not_refundable_default_message(self):
        """Ensure PaymentNotRefundable uses the expected default message."""
        exception = PaymentNotRefundable()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_IS_NOT_REFUNDABLE,
        )

    def test_refund_amount_exceeded_default_message(self):
        """Ensure RefundAmountExceeded uses the expected default message."""
        exception = RefundAmountExceeded()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_REFUND_AMOUNT_EXCEEDS_AVAILABLE_REFUNDABLE_BALANCE,
        )

    def test_invalid_refund_amount_default_message(self):
        """Ensure InvalidRefundAmount uses the expected default message."""
        exception = InvalidRefundAmount()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_INVALID_REFUND_AMOUNT,
        )

    def test_payment_transaction_not_found_default_message(self):
        """Ensure PaymentTransactionNotFound uses the expected default message."""
        exception = PaymentTransactionNotFound()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_TRANSACTION_NOT_FOUND,
        )

    def test_payment_transaction_not_allowed_default_message(self):
        """Ensure PaymentTransactionNotAllowed uses the expected default message."""
        exception = PaymentTransactionNotAllowed()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_TRANSACTION_NOT_ALLOWED,
        )

    def test_duplicate_payment_reference_default_message(self):
        """Ensure DuplicatePaymentReference uses the expected default message."""
        exception = DuplicatePaymentReference()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_REFERENCE_ALREADY_EXISTS,
        )

    def test_duplicate_idempotency_key_default_message(self):
        """Ensure DuplicateIdempotencyKey uses the expected default message."""
        exception = DuplicateIdempotencyKey()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_IDEMPOTENCY_KEY_ALREADY_BEEN_USED,
        )

    def test_payment_order_mismatch_default_message(self):
        """Ensure PaymentOrderMismatch uses the expected default message."""
        exception = PaymentOrderMismatch()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_DATA_DOES_NOT_MATCH,
        )

    def test_payment_customer_mismatch_default_message(self):
        """Ensure PaymentCustomerMismatch uses the expected default message."""
        exception = PaymentCustomerMismatch()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_CUSTOMER_DOES_NOT_MATCH,
        )

    def test_payment_amount_mismatch_default_message(self):
        """Ensure PaymentAmountMismatch uses the expected default message."""
        exception = PaymentAmountMismatch()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_AMOUNT_DOES_NOT_MATCH,
        )

    def test_refund_processing_failed_default_message(self):
        """Ensure RefundProcessingFailed uses the expected default message."""
        exception = RefundProcessingFailed()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_REFUND_PROCESSING_FAILED,
        )

    def test_payment_refund_not_found_default_message(self):
        """Ensure PaymentRefundNotFound uses the expected default message."""
        exception = PaymentRefundNotFound()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_REFUND_NOT_FOUND,
        )

    def test_refund_already_processed_default_message(self):
        """Ensure RefundAlreadyProcessed uses the expected default message."""
        exception = RefundAlreadyProcessed()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_PROCESSED,
        )

    def test_refund_already_cancelled_default_message(self):
        """Ensure RefundAlreadyCancelled uses the expected default message."""
        exception = RefundAlreadyCancelled()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_CANCELLED,
        )

    def test_refund_processing_not_allowed_default_message(self):
        """Ensure RefundProcessingNotAllowed uses the expected default message."""
        exception = RefundProcessingNotAllowed()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_PROCESSED,
        )

    def test_refund_cancellation_not_allowed_default_message(self):
        """Ensure RefundCancellationNotAllowed uses the expected default message."""
        exception = RefundCancellationNotAllowed()

        self.assertEqual(
            exception.message,
            MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_CANCELLED_IN_ITS_STATE,
        )

    def test_all_payment_exceptions_inherit_from_payment_error(self):
        """Ensure all payment-specific exceptions inherit from PaymentError."""
        exception_classes = [
            PaymentNotFound,
            PaymentPermissionDenied,
            PaymentCreationNotAllowed,
            PaymentAlreadyProcessed,
            PaymentProcessingNotAllowed,
            PaymentProcessingFailed,
            InvalidPaymentStatusTransition,
            PaymentCancellationNotAllowed,
            PaymentAlreadyCancelled,
            PaymentRefundNotAllowed,
            PaymentAlreadyRefunded,
            PaymentNotRefundable,
            RefundAmountExceeded,
            InvalidRefundAmount,
            PaymentTransactionNotFound,
            PaymentTransactionNotAllowed,
            DuplicatePaymentReference,
            DuplicateIdempotencyKey,
            PaymentOrderMismatch,
            PaymentCustomerMismatch,
            PaymentAmountMismatch,
            RefundProcessingFailed,
            PaymentRefundNotFound,
            RefundAlreadyProcessed,
            RefundAlreadyCancelled,
            RefundProcessingNotAllowed,
            RefundCancellationNotAllowed,
        ]

        for exception_class in exception_classes:
            with self.subTest(exception_class=exception_class.__name__):
                self.assertTrue(issubclass(exception_class, PaymentError))

    def test_exceptions_accept_custom_message_override(self):
        """Ensure payment exceptions accept a custom message override."""
        exception = PaymentNotFound("Custom not found message.")

        self.assertEqual(exception.message, "Custom not found message.")
        self.assertEqual(str(exception), "Custom not found message.")