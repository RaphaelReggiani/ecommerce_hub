from django.db import transaction
from django.utils import timezone

from ech.payments.exceptions import (
    PaymentAlreadyCancelled,
    PaymentAlreadyProcessed,
    PaymentNotFound,
    PaymentProcessingFailed,
    PaymentProcessingNotAllowed,
)
from ech.payments.models import (
    Payment, 
    PaymentTransaction,
)

from ech.payments.services.payment_status_service import PaymentStatusService

from ech.payments.constants.messages import (
    MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND,
    MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_CANCELLED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_PROCESSED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_PROCESSED,
    MSG_SERVICE_ERROR_PAYMENT_CANNOT_BE_CANCELLED_FROM_ITS_CURRENT_STATE,
    MSG_SERVICE_ERROR_ONLY_PAYMENTS_IN_PROCESSING_STATUS_CAN_BE_AUTHORIZED,
    MSG_SERVICE_ERROR_ONLY_PAYMENTS_IN_PROCESSING_OR_AUTHORIZED_CAN_BE_CAPTURED,
    MSG_SERVICE_ERROR_ONLY_PROCESSING_PAYMENTS_CAN_BE_CHARGED,
    MSG_SERVICE_ERROR_PAYMENT_CANNOT_BE_MARKED_AS_FAILED,
)


class PaymentProcessingService:
    """
    Service responsible for orchestrating payment processing flows.

    Responsibilities:
        - validate if a payment can be processed
        - start payment processing
        - register transaction attempts
        - finalize payment as authorized, captured, failed, or cancelled
        - update gateway-related fields when provided
    """

    @classmethod
    @transaction.atomic
    def start_processing(
        cls,
        *,
        payment: Payment,
        performed_by=None,
        metadata: dict | None = None,
    ) -> Payment:
        """
        Move a payment into processing state.

        Allowed only for pending payments.
        """

        cls._validate_can_start_processing(payment=payment)

        return PaymentStatusService.change_status(
            payment=payment,
            new_status=Payment.PAYMENT_STATUS_PROCESSING,
            performed_by=performed_by,
            metadata=metadata or {},
        )

    @classmethod
    @transaction.atomic
    def authorize_payment(
        cls,
        *,
        payment: Payment,
        performed_by=None,
        amount=None,
        gateway_transaction_id: str = "",
        gateway_response_code: str = "",
        gateway_response_message: str = "",
        metadata: dict | None = None,
    ) -> PaymentTransaction:
        """
        Register a successful authorization transaction
        and update the payment status to authorized.
        """

        cls._validate_can_authorize(payment=payment)

        transaction_record = PaymentTransaction.objects.create(
            payment=payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=amount if amount is not None else payment.amount,
            currency=payment.currency,
            gateway_transaction_id=gateway_transaction_id,
            gateway_response_code=gateway_response_code,
            gateway_response_message=gateway_response_message,
            metadata=metadata or {},
            performed_by=performed_by,
            processed_at=timezone.now(),
        )

        PaymentStatusService.change_status(
            payment=payment,
            new_status=Payment.PAYMENT_STATUS_AUTHORIZED,
            performed_by=performed_by,
            metadata={
                "transaction_id": str(transaction_record.id),
                "transaction_type": transaction_record.transaction_type,
                **(metadata or {}),
            },
        )

        return transaction_record

    @classmethod
    @transaction.atomic
    def capture_payment(
        cls,
        *,
        payment: Payment,
        performed_by=None,
        amount=None,
        gateway_transaction_id: str = "",
        gateway_response_code: str = "",
        gateway_response_message: str = "",
        metadata: dict | None = None,
    ) -> PaymentTransaction:
        """
        Register a successful capture transaction
        and update the payment status to captured.
        """

        cls._validate_can_capture(payment=payment)

        transaction_record = PaymentTransaction.objects.create(
            payment=payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_CAPTURE,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=amount if amount is not None else payment.amount,
            currency=payment.currency,
            gateway_transaction_id=gateway_transaction_id,
            gateway_response_code=gateway_response_code,
            gateway_response_message=gateway_response_message,
            metadata=metadata or {},
            performed_by=performed_by,
            processed_at=timezone.now(),
        )

        PaymentStatusService.change_status(
            payment=payment,
            new_status=Payment.PAYMENT_STATUS_CAPTURED,
            performed_by=performed_by,
            metadata={
                "transaction_id": str(transaction_record.id),
                "transaction_type": transaction_record.transaction_type,
                **(metadata or {}),
            },
        )

        return transaction_record

    @classmethod
    @transaction.atomic
    def charge_payment(
        cls,
        *,
        payment: Payment,
        performed_by=None,
        amount=None,
        gateway_transaction_id: str = "",
        gateway_response_code: str = "",
        gateway_response_message: str = "",
        metadata: dict | None = None,
    ) -> PaymentTransaction:
        """
        Register a direct charge transaction and mark the payment as captured.

        This is useful for payment methods or gateway flows
        where authorization and capture happen in a single step.
        """

        cls._validate_can_charge(payment=payment)

        transaction_record = PaymentTransaction.objects.create(
            payment=payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_CHARGE,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=amount if amount is not None else payment.amount,
            currency=payment.currency,
            gateway_transaction_id=gateway_transaction_id,
            gateway_response_code=gateway_response_code,
            gateway_response_message=gateway_response_message,
            metadata=metadata or {},
            performed_by=performed_by,
            processed_at=timezone.now(),
        )

        PaymentStatusService.change_status(
            payment=payment,
            new_status=Payment.PAYMENT_STATUS_CAPTURED,
            performed_by=performed_by,
            metadata={
                "transaction_id": str(transaction_record.id),
                "transaction_type": transaction_record.transaction_type,
                "charge_flow": True,
                **(metadata or {}),
            },
        )

        return transaction_record

    @classmethod
    @transaction.atomic
    def fail_payment(
        cls,
        *,
        payment: Payment,
        performed_by=None,
        failure_code: str = "",
        failure_message: str = "",
        gateway_transaction_id: str = "",
        gateway_response_code: str = "",
        gateway_response_message: str = "",
        metadata: dict | None = None,
    ) -> PaymentTransaction:
        """
        Register a failed processing attempt
        and update the payment status to failed.
        """

        cls._validate_can_fail(payment=payment)

        transaction_record = PaymentTransaction.objects.create(
            payment=payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_FAILURE,
            status=PaymentTransaction.TRANSACTION_STATUS_FAILED,
            amount=payment.amount,
            currency=payment.currency,
            gateway_transaction_id=gateway_transaction_id,
            gateway_response_code=gateway_response_code,
            gateway_response_message=gateway_response_message or failure_message,
            metadata=metadata or {},
            performed_by=performed_by,
            processed_at=timezone.now(),
        )

        payment.failure_code = failure_code
        payment.failure_message = failure_message
        payment.save(update_fields=["failure_code", "failure_message", "updated_at"])

        PaymentStatusService.change_status(
            payment=payment,
            new_status=Payment.PAYMENT_STATUS_FAILED,
            performed_by=performed_by,
            metadata={
                "transaction_id": str(transaction_record.id),
                "failure_code": failure_code,
                "failure_message": failure_message,
                **(metadata or {}),
            },
        )

        return transaction_record

    @classmethod
    @transaction.atomic
    def cancel_payment(
        cls,
        *,
        payment: Payment,
        performed_by=None,
        gateway_transaction_id: str = "",
        gateway_response_code: str = "",
        gateway_response_message: str = "",
        metadata: dict | None = None,
    ) -> PaymentTransaction:
        """
        Register a cancellation transaction
        and update the payment status to cancelled.
        """

        cls._validate_can_cancel(payment=payment)

        transaction_record = PaymentTransaction.objects.create(
            payment=payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_CANCELLATION,
            status=PaymentTransaction.TRANSACTION_STATUS_CANCELLED,
            amount=payment.amount,
            currency=payment.currency,
            gateway_transaction_id=gateway_transaction_id,
            gateway_response_code=gateway_response_code,
            gateway_response_message=gateway_response_message,
            metadata=metadata or {},
            performed_by=performed_by,
            processed_at=timezone.now(),
        )

        PaymentStatusService.change_status(
            payment=payment,
            new_status=Payment.PAYMENT_STATUS_CANCELLED,
            performed_by=performed_by,
            metadata={
                "transaction_id": str(transaction_record.id),
                "transaction_type": transaction_record.transaction_type,
                **(metadata or {}),
            },
        )

        return transaction_record

    @staticmethod
    def _validate_can_start_processing(*, payment: Payment) -> None:
        """
        Validate if a payment can move to processing.
        """

        if payment is None:
            raise PaymentNotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND)

        if payment.status == Payment.PAYMENT_STATUS_CANCELLED:
            raise PaymentAlreadyCancelled(MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_CANCELLED)

        if payment.status in {
            Payment.PAYMENT_STATUS_AUTHORIZED,
            Payment.PAYMENT_STATUS_CAPTURED,
            Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
            Payment.PAYMENT_STATUS_REFUNDED,
        }:
            raise PaymentAlreadyProcessed(MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_PROCESSED)

        if payment.status != Payment.PAYMENT_STATUS_PENDING:
            raise PaymentProcessingNotAllowed(MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_PROCESSED)

    @staticmethod
    def _validate_can_authorize(*, payment: Payment) -> None:
        """
        Validate if a payment can be authorized.
        """

        if payment.status != Payment.PAYMENT_STATUS_PROCESSING:
            raise PaymentProcessingNotAllowed(MSG_SERVICE_ERROR_ONLY_PAYMENTS_IN_PROCESSING_STATUS_CAN_BE_AUTHORIZED)

    @staticmethod
    def _validate_can_capture(*, payment: Payment) -> None:
        """
        Validate if a payment can be captured.
        """

        if payment.status not in {
            Payment.PAYMENT_STATUS_PROCESSING,
            Payment.PAYMENT_STATUS_AUTHORIZED,
        }:
            raise PaymentProcessingNotAllowed(MSG_SERVICE_ERROR_ONLY_PAYMENTS_IN_PROCESSING_OR_AUTHORIZED_CAN_BE_CAPTURED)

    @staticmethod
    def _validate_can_charge(*, payment: Payment) -> None:
        """
        Validate if a payment can be directly charged.
        """

        if payment.status != Payment.PAYMENT_STATUS_PROCESSING:
            raise PaymentProcessingNotAllowed(MSG_SERVICE_ERROR_ONLY_PROCESSING_PAYMENTS_CAN_BE_CHARGED)

    @staticmethod
    def _validate_can_fail(*, payment: Payment) -> None:
        """
        Validate if a payment can be marked as failed.
        """

        if payment.status in {
            Payment.PAYMENT_STATUS_CAPTURED,
            Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
            Payment.PAYMENT_STATUS_REFUNDED,
            Payment.PAYMENT_STATUS_CANCELLED,
        }:
            raise PaymentProcessingNotAllowed(MSG_SERVICE_ERROR_PAYMENT_CANNOT_BE_MARKED_AS_FAILED)

    @staticmethod
    def _validate_can_cancel(*, payment: Payment) -> None:
        """
        Validate if a payment can be cancelled.
        """

        if payment.status == Payment.PAYMENT_STATUS_CANCELLED:
            raise PaymentAlreadyCancelled(MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_CANCELLED)

        if payment.status in {
            Payment.PAYMENT_STATUS_CAPTURED,
            Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
            Payment.PAYMENT_STATUS_REFUNDED,
            Payment.PAYMENT_STATUS_FAILED,
        }:
            raise PaymentProcessingNotAllowed(MSG_SERVICE_ERROR_PAYMENT_CANNOT_BE_CANCELLED_FROM_ITS_CURRENT_STATE)