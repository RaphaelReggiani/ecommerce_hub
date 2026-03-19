from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from ech.payments.exceptions import (
    InvalidRefundAmount,
    PaymentAlreadyRefunded,
    PaymentNotRefundable,
    RefundAlreadyCancelled,
    RefundAlreadyProcessed,
    RefundAmountExceeded,
    RefundCancellationNotAllowed,
    RefundProcessingNotAllowed,
)
from ech.payments.models import (
    Payment,
    PaymentRefund,
    PaymentTransaction,
)
from ech.payments.services.payment_log_service import PaymentLogService
from ech.payments.services.payment_status_service import PaymentStatusService

from ech.payments.domain_events.dispatcher import payment_event_dispatcher
from ech.payments.domain_events.events import (
    PaymentRefundCancelledEvent,
    PaymentRefundFailedEvent,
    PaymentRefundRequestedEvent,
)

from ech.payments.constants.messages import (
    MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_REFUNDED,
    MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_PROCESSED,
    MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_CANCELLED,
    MSG_SERVICE_ERROR_ONLY_CAPTURED_OR_PARTIALLY_REFUNDED_PAYMENTS_CAN_BE_REFUNDED,
    MSG_SERVICE_ERROR_REFUND_AMOUNT_EXCEEDS_REMAINING_REFUNDABLE_AMOUNT,
    MSG_SERVICE_ERROR_REFUND_AMOUNT_MUST_BE_GREATER,
    MSG_SERVICE_ERROR_ONLY_PENDING_REFUNDS_CAN_BE_PROCESSED,
    MSG_SERVICE_ERROR_PROCESSED_REFUNDS_CANNOT_BE_MARKED_AS_FAILED,
    MSG_SERVICE_ERROR_CANCELLED_REFUNDS_CANNOT_BE_MARKED_AS_FAILED,
    MSG_SERVICE_ERROR_ONLY_PENDING_REFUNDS_CAN_BE_MARKED_AS_FAILED,
    MSG_SERVICE_ERROR_PROCESSED_REFUNDS_CANNOT_BE_CANCELLED,
    MSG_SERVICE_ERROR_ONLY_PENDING_REFUNDS_CAN_BE_CANCELLED,
)


class PaymentRefundService:
    """
    Service responsible for handling payment refunds.

    Responsibilities:
        - validate refund request eligibility
        - create refund requests
        - process pending refunds
        - fail pending refunds
        - cancel pending refunds
        - update refunded amount only when refund is processed
        - update payment status (partial/full) only when refund is processed
        - maintain audit logs
    """

    @classmethod
    @transaction.atomic
    def request_refund(
        cls,
        *,
        payment: Payment,
        amount: Decimal,
        reason: str,
        performed_by=None,
        gateway_refund_id: str = "",
        metadata: dict | None = None,
    ) -> PaymentRefund:
        """
        Create a refund request for a payment.

        This method only creates the refund request with pending status.
        It does not process the refund yet.
        """

        cls._validate_refund_request(payment=payment, amount=amount)

        refund = PaymentRefund.objects.create(
            payment=payment,
            amount=amount,
            reason=reason,
            status=PaymentRefund.REFUND_STATUS_PENDING,
            gateway_refund_id=gateway_refund_id,
            metadata=metadata or {},
            requested_by=performed_by,
        )

        PaymentLogService.log_refund_requested(
            payment=payment,
            performed_by=performed_by,
            metadata={
                "refund_id": str(refund.id),
                "amount": str(refund.amount),
                "reason": refund.reason,
                **(metadata or {}),
            },
        )

        payment_event_dispatcher.dispatch(
            PaymentRefundRequestedEvent(
                payment_id=payment.id,
                refund_id=refund.id,
                amount=str(refund.amount),
                reason=refund.reason,
                metadata=metadata or {},
            )
        )

        return refund

    @classmethod
    @transaction.atomic
    def process_refund(
        cls,
        *,
        refund: PaymentRefund,
        performed_by=None,
        gateway_transaction_id: str = "",
        metadata: dict | None = None,
    ) -> PaymentRefund:
        """
        Process a pending refund request.

        This method:
            - validates refund processability
            - creates the refund transaction
            - updates payment refunded amount
            - marks refund as processed
            - updates payment status
        """

        cls._validate_refund_can_be_processed(refund=refund)

        payment = refund.payment
        cls._validate_refund_request(
            payment=payment,
            amount=refund.amount,
        )

        remaining_before_processing = cls._get_remaining_amount(payment)

        transaction_type = (
            PaymentTransaction.TRANSACTION_TYPE_REFUND
            if refund.amount == remaining_before_processing
            else PaymentTransaction.TRANSACTION_TYPE_PARTIAL_REFUND
        )

        transaction_record = PaymentTransaction.objects.create(
            payment=payment,
            transaction_type=transaction_type,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=refund.amount,
            currency=payment.currency,
            gateway_transaction_id=gateway_transaction_id,
            metadata=metadata or {},
            performed_by=performed_by,
            processed_at=timezone.now(),
        )

        payment.refunded_amount += refund.amount
        payment.save(update_fields=["refunded_amount", "updated_at"])

        refund.status = PaymentRefund.REFUND_STATUS_PROCESSED
        refund.processed_at = timezone.now()

        if hasattr(refund, "processed_by_id"):
            refund.processed_by = performed_by

        update_fields = ["status", "processed_at", "updated_at"]

        if hasattr(refund, "processed_by_id"):
            update_fields.append("processed_by")

        refund.save(update_fields=update_fields)

        cls._update_payment_status_after_refund(
            payment=payment,
            refund=refund,
            performed_by=performed_by,
            transaction_record=transaction_record,
            metadata=metadata,
        )

        return refund

    @classmethod
    @transaction.atomic
    def fail_refund(
        cls,
        *,
        refund: PaymentRefund,
        performed_by=None,
        metadata: dict | None = None,
    ) -> PaymentRefund:
        """
        Mark a pending refund as failed.

        This does not change payment refunded amount
        and does not change payment status.
        """

        cls._validate_refund_can_be_failed(refund=refund)

        refund.status = PaymentRefund.REFUND_STATUS_FAILED

        if metadata:
            refund.metadata = {
                **(refund.metadata or {}),
                **metadata,
            }

        refund.save(update_fields=["status", "metadata", "updated_at"])

        if hasattr(PaymentLogService, "log_refund_failed"):
            PaymentLogService.log_refund_failed(
                payment=refund.payment,
                performed_by=performed_by,
                metadata={
                    "refund_id": str(refund.id),
                    "amount": str(refund.amount),
                    **(metadata or {}),
                },
            )

            payment_event_dispatcher.dispatch(
                PaymentRefundFailedEvent(
                    payment_id=refund.payment_id,
                    refund_id=refund.id,
                    amount=str(refund.amount),
                    reason=refund.reason,
                    metadata=metadata or {},
                )
            )

        return refund

    @classmethod
    @transaction.atomic
    def cancel_refund(
        cls,
        *,
        refund: PaymentRefund,
        performed_by=None,
        metadata: dict | None = None,
    ) -> PaymentRefund:
        """
        Cancel a pending refund request.

        This does not change payment refunded amount
        and does not change payment status.
        """

        cls._validate_refund_can_be_cancelled(refund=refund)

        refund.status = PaymentRefund.REFUND_STATUS_CANCELLED

        if metadata:
            refund.metadata = {
                **(refund.metadata or {}),
                **metadata,
            }

        refund.save(update_fields=["status", "metadata", "updated_at"])

        if hasattr(PaymentLogService, "log_refund_cancelled"):
            PaymentLogService.log_refund_cancelled(
                payment=refund.payment,
                performed_by=performed_by,
                metadata={
                    "refund_id": str(refund.id),
                    "amount": str(refund.amount),
                    **(metadata or {}),
                },
            )

            payment_event_dispatcher.dispatch(
                PaymentRefundCancelledEvent(
                    payment_id=refund.payment_id,
                    refund_id=refund.id,
                    amount=str(refund.amount),
                    reason=refund.reason,
                    metadata=metadata or {},
                )
            )

        return refund

    @staticmethod
    def _validate_refund_request(*, payment: Payment, amount: Decimal) -> None:
        """
        Validate if a refund can be requested for the payment
        and if the requested amount is valid.
        """

        if payment.status not in {
            Payment.PAYMENT_STATUS_CAPTURED,
            Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
        }:
            raise PaymentNotRefundable(MSG_SERVICE_ERROR_ONLY_CAPTURED_OR_PARTIALLY_REFUNDED_PAYMENTS_CAN_BE_REFUNDED)

        if payment.status == Payment.PAYMENT_STATUS_REFUNDED:
            raise PaymentAlreadyRefunded(MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_REFUNDED)

        if amount <= Decimal("0"):
            raise InvalidRefundAmount(MSG_SERVICE_ERROR_REFUND_AMOUNT_MUST_BE_GREATER)

        remaining = PaymentRefundService._get_remaining_amount(payment)

        if amount > remaining:
            raise RefundAmountExceeded(MSG_SERVICE_ERROR_REFUND_AMOUNT_EXCEEDS_REMAINING_REFUNDABLE_AMOUNT)

    @staticmethod
    def _validate_refund_can_be_processed(*, refund: PaymentRefund) -> None:
        """
        Validate if a refund request can be processed.
        """

        if refund.status == PaymentRefund.REFUND_STATUS_PROCESSED:
            raise RefundAlreadyProcessed(
                MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_PROCESSED
            )

        if refund.status == PaymentRefund.REFUND_STATUS_CANCELLED:
            raise RefundAlreadyCancelled(
                MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_CANCELLED
            )

        if refund.status != PaymentRefund.REFUND_STATUS_PENDING:
            raise RefundProcessingNotAllowed(
                MSG_SERVICE_ERROR_ONLY_PENDING_REFUNDS_CAN_BE_PROCESSED
            )

    @staticmethod
    def _validate_refund_can_be_failed(*, refund: PaymentRefund) -> None:
        """
        Validate if a refund request can be marked as failed.
        """

        if refund.status == PaymentRefund.REFUND_STATUS_PROCESSED:
            raise RefundAlreadyProcessed(MSG_SERVICE_ERROR_PROCESSED_REFUNDS_CANNOT_BE_MARKED_AS_FAILED)

        if refund.status == PaymentRefund.REFUND_STATUS_CANCELLED:
            raise RefundAlreadyCancelled(MSG_SERVICE_ERROR_CANCELLED_REFUNDS_CANNOT_BE_MARKED_AS_FAILED)

        if refund.status != PaymentRefund.REFUND_STATUS_PENDING:
            raise RefundProcessingNotAllowed(MSG_SERVICE_ERROR_ONLY_PENDING_REFUNDS_CAN_BE_MARKED_AS_FAILED)

    @staticmethod
    def _validate_refund_can_be_cancelled(*, refund: PaymentRefund) -> None:
        """
        Validate if a refund request can be cancelled.
        """

        if refund.status == PaymentRefund.REFUND_STATUS_CANCELLED:
            raise RefundAlreadyCancelled(
                MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_CANCELLED
            )

        if refund.status == PaymentRefund.REFUND_STATUS_PROCESSED:
            raise RefundCancellationNotAllowed(MSG_SERVICE_ERROR_PROCESSED_REFUNDS_CANNOT_BE_CANCELLED)

        if refund.status != PaymentRefund.REFUND_STATUS_PENDING:
            raise RefundCancellationNotAllowed(MSG_SERVICE_ERROR_ONLY_PENDING_REFUNDS_CAN_BE_CANCELLED)

    @staticmethod
    def _get_remaining_amount(payment: Payment) -> Decimal:
        """
        Return the remaining refundable amount for the payment.
        """

        return payment.amount - payment.refunded_amount

    @classmethod
    def _update_payment_status_after_refund(
        cls,
        *,
        payment: Payment,
        refund: PaymentRefund,
        performed_by=None,
        transaction_record: PaymentTransaction,
        metadata: dict | None = None,
    ) -> None:
        """
        Update payment status after a successful refund processing.
        """

        if payment.refunded_amount == payment.amount:
            PaymentStatusService.change_status(
                payment=payment,
                new_status=Payment.PAYMENT_STATUS_REFUNDED,
                performed_by=performed_by,
                metadata={
                    "refund_id": str(refund.id),
                    "transaction_id": str(transaction_record.id),
                    "amount": str(refund.amount),
                    "full_refund": True,
                    "refunded_amount": str(payment.refunded_amount),
                    **(metadata or {}),
                },
            )
        else:
            PaymentStatusService.change_status(
                payment=payment,
                new_status=Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
                performed_by=performed_by,
                metadata={
                    "refund_id": str(refund.id),
                    "transaction_id": str(transaction_record.id),
                    "amount": str(refund.amount),
                    "partial_refund": True,
                    "refunded_amount": str(payment.refunded_amount),
                    **(metadata or {}),
                },
            )