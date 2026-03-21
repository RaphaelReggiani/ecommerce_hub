from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from ech.orders.models import Order
from ech.payments.exceptions import (
    PaymentAlreadyCancelled,
    PaymentAlreadyProcessed,
    PaymentNotFound,
    PaymentProcessingNotAllowed,
)
from ech.payments.models import Payment, PaymentTransaction
from ech.payments.services.payment_processing_service import PaymentProcessingService
from ech.users.models import CustomUser


class PaymentProcessingServiceTestCase(TestCase):

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
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        self.payment = Payment.objects.create(
            order=self.order,
            customer=self.customer,
            payment_reference="PAY-001",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("100.00"),
        )

    @patch("ech.payments.services.payment_processing_service.PaymentStatusService.change_status")
    def test_start_processing_success(self, mock_status):
        """Ensure pending payment can move to processing."""
        mock_status.return_value = self.payment

        PaymentProcessingService.start_processing(
            payment=self.payment,
            performed_by=self.actor,
        )

        mock_status.assert_called_once()

    def test_start_processing_raises_if_payment_none(self):
        """Ensure start_processing raises when payment is None."""
        with self.assertRaises(PaymentNotFound):
            PaymentProcessingService._validate_can_start_processing(payment=None)

    def test_start_processing_raises_if_cancelled(self):
        """Ensure cancelled payment cannot start processing."""
        self.payment.status = Payment.PAYMENT_STATUS_CANCELLED

        with self.assertRaises(PaymentAlreadyCancelled):
            PaymentProcessingService._validate_can_start_processing(payment=self.payment)

    def test_start_processing_raises_if_already_processed(self):
        """Ensure processed payments cannot restart processing."""
        self.payment.status = Payment.PAYMENT_STATUS_CAPTURED

        with self.assertRaises(PaymentAlreadyProcessed):
            PaymentProcessingService._validate_can_start_processing(payment=self.payment)

    def test_authorize_payment_success(self):
        """Ensure authorization transaction is created and status updated."""
        self.payment.status = Payment.PAYMENT_STATUS_PROCESSING
        self.payment.save()

        with patch("ech.payments.services.payment_processing_service.PaymentStatusService.change_status"):
            transaction = PaymentProcessingService.authorize_payment(
                payment=self.payment,
                performed_by=self.actor,
            )

        self.assertEqual(transaction.transaction_type, PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION)
        self.assertEqual(transaction.status, PaymentTransaction.TRANSACTION_STATUS_SUCCESS)

    def test_authorize_payment_invalid_state(self):
        """Ensure authorize fails if payment not processing."""
        with self.assertRaises(PaymentProcessingNotAllowed):
            PaymentProcessingService.authorize_payment(payment=self.payment)

    def test_capture_payment_success(self):
        """Ensure capture transaction is created."""
        self.payment.status = Payment.PAYMENT_STATUS_AUTHORIZED
        self.payment.save()

        with patch("ech.payments.services.payment_processing_service.PaymentStatusService.change_status"):
            transaction = PaymentProcessingService.capture_payment(
                payment=self.payment,
                performed_by=self.actor,
            )

        self.assertEqual(transaction.transaction_type, PaymentTransaction.TRANSACTION_TYPE_CAPTURE)

    def test_capture_payment_invalid_state(self):
        """Ensure capture fails for invalid states."""
        with self.assertRaises(PaymentProcessingNotAllowed):
            PaymentProcessingService.capture_payment(payment=self.payment)

    def test_charge_payment_success(self):
        """Ensure direct charge transaction works."""
        self.payment.status = Payment.PAYMENT_STATUS_PROCESSING
        self.payment.save()

        with patch("ech.payments.services.payment_processing_service.PaymentStatusService.change_status"):
            transaction = PaymentProcessingService.charge_payment(
                payment=self.payment,
                performed_by=self.actor,
            )

        self.assertEqual(transaction.transaction_type, PaymentTransaction.TRANSACTION_TYPE_CHARGE)

    def test_charge_payment_invalid_state(self):
        """Ensure charge fails outside processing state."""
        with self.assertRaises(PaymentProcessingNotAllowed):
            PaymentProcessingService.charge_payment(payment=self.payment)

    def test_fail_payment_success(self):
        """Ensure failure transaction is created and failure fields updated."""
        with patch("ech.payments.services.payment_processing_service.PaymentStatusService.change_status"):
            transaction = PaymentProcessingService.fail_payment(
                payment=self.payment,
                performed_by=self.actor,
                failure_code="DECLINED",
                failure_message="Card declined",
            )

        self.assertEqual(transaction.transaction_type, PaymentTransaction.TRANSACTION_TYPE_FAILURE)

        self.payment.refresh_from_db()

        self.assertEqual(self.payment.failure_code, "DECLINED")
        self.assertEqual(self.payment.failure_message, "Card declined")

    def test_fail_payment_invalid_state(self):
        """Ensure captured payments cannot be marked as failed."""
        self.payment.status = Payment.PAYMENT_STATUS_CAPTURED

        with self.assertRaises(PaymentProcessingNotAllowed):
            PaymentProcessingService.fail_payment(payment=self.payment)

    def test_cancel_payment_success(self):
        """Ensure cancel transaction is created."""
        with patch("ech.payments.services.payment_processing_service.PaymentStatusService.change_status"):
            transaction = PaymentProcessingService.cancel_payment(
                payment=self.payment,
                performed_by=self.actor,
            )

        self.assertEqual(transaction.transaction_type, PaymentTransaction.TRANSACTION_TYPE_CANCELLATION)

    def test_cancel_payment_already_cancelled(self):
        """Ensure cancelling twice raises error."""
        self.payment.status = Payment.PAYMENT_STATUS_CANCELLED

        with self.assertRaises(PaymentAlreadyCancelled):
            PaymentProcessingService.cancel_payment(payment=self.payment)

    def test_cancel_payment_invalid_state(self):
        """Ensure captured payments cannot be cancelled."""
        self.payment.status = Payment.PAYMENT_STATUS_CAPTURED

        with self.assertRaises(PaymentProcessingNotAllowed):
            PaymentProcessingService.cancel_payment(payment=self.payment)