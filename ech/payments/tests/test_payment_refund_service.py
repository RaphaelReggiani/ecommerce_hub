from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from ech.orders.models import Order
from ech.payments.exceptions import (
    InvalidRefundAmount,
    PaymentNotRefundable,
    RefundAlreadyCancelled,
    RefundAlreadyProcessed,
    RefundAmountExceeded,
    RefundCancellationNotAllowed,
    RefundProcessingNotAllowed,
)
from ech.payments.models import Payment, PaymentRefund, PaymentTransaction
from ech.payments.services.payment_refund_service import PaymentRefundService
from ech.users.models import CustomUser


class PaymentRefundServiceTestCase(TestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.actor = CustomUser.objects.create_user(
            email="actor@test.com",
            password="StrongPassword123",
            user_name="Actor",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.order = Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_CAPTURED,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        self.payment = Payment.objects.create(
            order=self.order,
            customer=self.customer,
            payment_reference="PAY-001",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_CAPTURED,
            amount=Decimal("100.00"),
            refunded_amount=Decimal("0.00"),
        )

    @patch("ech.payments.services.payment_refund_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_refund_service.PaymentLogService.log_refund_requested")
    def test_request_refund_success(self, mock_log, mock_dispatch):
        """Ensure refund request is created with pending status."""
        refund = PaymentRefundService.request_refund(
            payment=self.payment,
            amount=Decimal("20.00"),
            reason="Customer request",
            performed_by=self.actor,
            gateway_refund_id="gw_ref_1",
            metadata={"source": "test"},
        )

        self.assertEqual(refund.payment, self.payment)
        self.assertEqual(refund.amount, Decimal("20.00"))
        self.assertEqual(refund.reason, "Customer request")
        self.assertEqual(refund.status, PaymentRefund.REFUND_STATUS_PENDING)
        self.assertEqual(refund.gateway_refund_id, "gw_ref_1")
        self.assertEqual(refund.requested_by, self.actor)

        mock_log.assert_called_once()
        mock_dispatch.assert_called_once()

    def test_request_refund_raises_for_invalid_payment_status(self):
        """Ensure refund request fails for non-refundable payment status."""
        self.payment.status = Payment.PAYMENT_STATUS_PENDING

        with self.assertRaises(PaymentNotRefundable):
            PaymentRefundService.request_refund(
                payment=self.payment,
                amount=Decimal("10.00"),
                reason="Invalid status",
            )

    def test_request_refund_raises_for_already_refunded_amount_exceeded_path(self):
        """Ensure fully refunded payment cannot receive another refund request."""
        self.payment.status = Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED
        self.payment.refunded_amount = Decimal("100.00")

        with self.assertRaises(RefundAmountExceeded):
            PaymentRefundService.request_refund(
                payment=self.payment,
                amount=Decimal("1.00"),
                reason="Exceeded",
            )

    def test_request_refund_raises_for_zero_or_negative_amount(self):
        """Ensure refund request rejects zero or negative amounts."""
        with self.assertRaises(InvalidRefundAmount):
            PaymentRefundService.request_refund(
                payment=self.payment,
                amount=Decimal("0.00"),
                reason="Zero refund",
            )

        with self.assertRaises(InvalidRefundAmount):
            PaymentRefundService.request_refund(
                payment=self.payment,
                amount=Decimal("-5.00"),
                reason="Negative refund",
            )

    def test_request_refund_raises_when_amount_exceeds_remaining(self):
        """Ensure refund request rejects amount greater than remaining refundable amount."""
        self.payment.refunded_amount = Decimal("30.00")
        self.payment.status = Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED

        with self.assertRaises(RefundAmountExceeded):
            PaymentRefundService.request_refund(
                payment=self.payment,
                amount=Decimal("80.00"),
                reason="Too much",
            )

    @patch("ech.payments.services.payment_refund_service.PaymentStatusService.change_status")
    def test_process_refund_success_partial_refund(self, mock_change_status):
        """Ensure processing a partial refund updates records and payment status."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("20.00"),
            reason="Partial refund",
            status=PaymentRefund.REFUND_STATUS_PENDING,
            requested_by=self.actor,
        )

        result = PaymentRefundService.process_refund(
            refund=refund,
            performed_by=self.actor,
            gateway_transaction_id="tx_ref_1",
            metadata={"source": "test"},
        )

        self.payment.refresh_from_db()
        refund.refresh_from_db()

        transaction = PaymentTransaction.objects.get(payment=self.payment)

        self.assertEqual(result.status, PaymentRefund.REFUND_STATUS_PROCESSED)
        self.assertEqual(self.payment.refunded_amount, Decimal("20.00"))
        self.assertEqual(transaction.transaction_type, PaymentTransaction.TRANSACTION_TYPE_PARTIAL_REFUND)
        self.assertEqual(transaction.status, PaymentTransaction.TRANSACTION_STATUS_SUCCESS)
        self.assertEqual(transaction.gateway_transaction_id, "tx_ref_1")
        self.assertEqual(refund.processed_by, self.actor)
        self.assertIsNotNone(refund.processed_at)

        mock_change_status.assert_called_once()

    @patch("ech.payments.services.payment_refund_service.PaymentStatusService.change_status")
    def test_process_refund_success_full_refund(self, mock_change_status):
        """Ensure processing a full refund creates full refund transaction."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("100.00"),
            reason="Full refund",
            status=PaymentRefund.REFUND_STATUS_PENDING,
            requested_by=self.actor,
        )

        PaymentRefundService.process_refund(
            refund=refund,
            performed_by=self.actor,
            gateway_transaction_id="tx_ref_full",
        )

        self.payment.refresh_from_db()
        refund.refresh_from_db()

        transaction = PaymentTransaction.objects.get(payment=self.payment)

        self.assertEqual(self.payment.refunded_amount, Decimal("100.00"))
        self.assertEqual(refund.status, PaymentRefund.REFUND_STATUS_PROCESSED)
        self.assertEqual(transaction.transaction_type, PaymentTransaction.TRANSACTION_TYPE_REFUND)

        mock_change_status.assert_called_once()

    def test_process_refund_raises_if_already_processed(self):
        """Ensure processed refunds cannot be processed again."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("10.00"),
            reason="Processed",
            status=PaymentRefund.REFUND_STATUS_PROCESSED,
        )

        with self.assertRaises(RefundAlreadyProcessed):
            PaymentRefundService.process_refund(refund=refund)

    def test_process_refund_raises_if_cancelled(self):
        """Ensure cancelled refunds cannot be processed."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("10.00"),
            reason="Cancelled",
            status=PaymentRefund.REFUND_STATUS_CANCELLED,
        )

        with self.assertRaises(RefundAlreadyCancelled):
            PaymentRefundService.process_refund(refund=refund)

    def test_process_refund_raises_if_not_pending(self):
        """Ensure only pending refunds can be processed."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("10.00"),
            reason="Failed",
            status=PaymentRefund.REFUND_STATUS_FAILED,
        )

        with self.assertRaises(RefundProcessingNotAllowed):
            PaymentRefundService.process_refund(refund=refund)

    @patch("ech.payments.services.payment_refund_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_refund_service.PaymentLogService.log_refund_failed")
    def test_fail_refund_success(self, mock_log, mock_dispatch):
        """Ensure pending refund can be marked as failed."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("15.00"),
            reason="Fail refund",
            status=PaymentRefund.REFUND_STATUS_PENDING,
            metadata={"initial": "value"},
        )

        result = PaymentRefundService.fail_refund(
            refund=refund,
            performed_by=self.actor,
            metadata={"reason_code": "gateway_error"},
        )

        result.refresh_from_db()

        self.assertEqual(result.status, PaymentRefund.REFUND_STATUS_FAILED)
        self.assertEqual(
            result.metadata,
            {"initial": "value", "reason_code": "gateway_error"},
        )

        mock_log.assert_called_once()
        mock_dispatch.assert_called_once()

    def test_fail_refund_raises_if_processed(self):
        """Ensure processed refund cannot be marked as failed."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("15.00"),
            reason="Processed refund",
            status=PaymentRefund.REFUND_STATUS_PROCESSED,
        )

        with self.assertRaises(RefundAlreadyProcessed):
            PaymentRefundService.fail_refund(refund=refund)

    def test_fail_refund_raises_if_cancelled(self):
        """Ensure cancelled refund cannot be marked as failed."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("15.00"),
            reason="Cancelled refund",
            status=PaymentRefund.REFUND_STATUS_CANCELLED,
        )

        with self.assertRaises(RefundAlreadyCancelled):
            PaymentRefundService.fail_refund(refund=refund)

    def test_fail_refund_raises_if_not_pending(self):
        """Ensure only pending refunds can be marked as failed."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("15.00"),
            reason="Already failed",
            status=PaymentRefund.REFUND_STATUS_FAILED,
        )

        with self.assertRaises(RefundProcessingNotAllowed):
            PaymentRefundService.fail_refund(refund=refund)

    @patch("ech.payments.services.payment_refund_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_refund_service.PaymentLogService.log_refund_cancelled")
    def test_cancel_refund_success(self, mock_log, mock_dispatch):
        """Ensure pending refund can be cancelled."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("12.00"),
            reason="Cancel refund",
            status=PaymentRefund.REFUND_STATUS_PENDING,
            metadata={"initial": "value"},
        )

        result = PaymentRefundService.cancel_refund(
            refund=refund,
            performed_by=self.actor,
            metadata={"cancel_reason": "user_request"},
        )

        result.refresh_from_db()

        self.assertEqual(result.status, PaymentRefund.REFUND_STATUS_CANCELLED)
        self.assertEqual(
            result.metadata,
            {"initial": "value", "cancel_reason": "user_request"},
        )

        mock_log.assert_called_once()
        mock_dispatch.assert_called_once()

    def test_cancel_refund_raises_if_already_cancelled(self):
        """Ensure already cancelled refund cannot be cancelled again."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("12.00"),
            reason="Cancelled refund",
            status=PaymentRefund.REFUND_STATUS_CANCELLED,
        )

        with self.assertRaises(RefundAlreadyCancelled):
            PaymentRefundService.cancel_refund(refund=refund)

    def test_cancel_refund_raises_if_processed(self):
        """Ensure processed refund cannot be cancelled."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("12.00"),
            reason="Processed refund",
            status=PaymentRefund.REFUND_STATUS_PROCESSED,
        )

        with self.assertRaises(RefundCancellationNotAllowed):
            PaymentRefundService.cancel_refund(refund=refund)

    def test_cancel_refund_raises_if_not_pending(self):
        """Ensure only pending refunds can be cancelled."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("12.00"),
            reason="Failed refund",
            status=PaymentRefund.REFUND_STATUS_FAILED,
        )

        with self.assertRaises(RefundCancellationNotAllowed):
            PaymentRefundService.cancel_refund(refund=refund)

    def test_get_remaining_amount_returns_expected_value(self):
        """Ensure remaining refundable amount is calculated correctly."""
        self.payment.refunded_amount = Decimal("35.00")

        remaining = PaymentRefundService._get_remaining_amount(self.payment)

        self.assertEqual(remaining, Decimal("65.00"))

    @patch("ech.payments.services.payment_refund_service.PaymentStatusService.change_status")
    def test_update_payment_status_after_refund_sets_refunded(self, mock_change_status):
        """Ensure full refund triggers refunded payment status."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("100.00"),
            reason="Full refund",
            status=PaymentRefund.REFUND_STATUS_PENDING,
        )
        transaction = PaymentTransaction.objects.create(
            payment=self.payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_REFUND,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=Decimal("100.00"),
            currency=self.payment.currency,
        )

        self.payment.refunded_amount = Decimal("100.00")

        PaymentRefundService._update_payment_status_after_refund(
            payment=self.payment,
            refund=refund,
            performed_by=self.actor,
            transaction_record=transaction,
            metadata={"source": "test"},
        )

        mock_change_status.assert_called_once()

    @patch("ech.payments.services.payment_refund_service.PaymentStatusService.change_status")
    def test_update_payment_status_after_refund_sets_partially_refunded(self, mock_change_status):
        """Ensure partial refund triggers partially refunded payment status."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("20.00"),
            reason="Partial refund",
            status=PaymentRefund.REFUND_STATUS_PENDING,
        )
        transaction = PaymentTransaction.objects.create(
            payment=self.payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_PARTIAL_REFUND,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=Decimal("20.00"),
            currency=self.payment.currency,
        )

        self.payment.refunded_amount = Decimal("20.00")

        PaymentRefundService._update_payment_status_after_refund(
            payment=self.payment,
            refund=refund,
            performed_by=self.actor,
            transaction_record=transaction,
            metadata={"source": "test"},
        )

        mock_change_status.assert_called_once()

    def test_validate_refund_request_accepts_captured_payment(self):
        """Ensure refund request validation accepts captured payment."""
        PaymentRefundService._validate_refund_request(
            payment=self.payment,
            amount=Decimal("10.00"),
        )

    def test_validate_refund_request_accepts_partially_refunded_payment(self):
        """Ensure refund request validation accepts partially refunded payment."""
        self.payment.status = Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED
        self.payment.refunded_amount = Decimal("20.00")

        PaymentRefundService._validate_refund_request(
            payment=self.payment,
            amount=Decimal("10.00"),
        )

    def test_validate_refund_request_raises_for_fully_refunded_status(self):
        """Ensure refund request validation rejects refunded payment status."""
        self.payment.status = Payment.PAYMENT_STATUS_REFUNDED

        with self.assertRaises(PaymentNotRefundable):
            PaymentRefundService._validate_refund_request(
                payment=self.payment,
                amount=Decimal("10.00"),
            )