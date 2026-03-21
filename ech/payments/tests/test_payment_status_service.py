from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from ech.orders.models import Order, OrderLifecycle
from ech.payments.exceptions import InvalidPaymentStatusTransition
from ech.payments.models import Payment, PaymentLifecycle
from ech.payments.services.payment_status_service import PaymentStatusService
from ech.users.models import CustomUser


class PaymentStatusServiceTestCase(TestCase):
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

        self.lifecycle = PaymentLifecycle.objects.create(payment=self.payment)

    def test_validate_transition_allows_same_status(self):
        """Ensure transition validation allows same current and new status."""
        PaymentStatusService._validate_transition(
            current_status=Payment.PAYMENT_STATUS_PENDING,
            new_status=Payment.PAYMENT_STATUS_PENDING,
        )

    def test_validate_transition_allows_valid_transition(self):
        """Ensure transition validation allows configured valid transition."""
        PaymentStatusService._validate_transition(
            current_status=Payment.PAYMENT_STATUS_PENDING,
            new_status=Payment.PAYMENT_STATUS_PROCESSING,
        )

    def test_validate_transition_raises_for_invalid_transition(self):
        """Ensure transition validation raises for invalid status change."""
        with self.assertRaises(InvalidPaymentStatusTransition):
            PaymentStatusService._validate_transition(
                current_status=Payment.PAYMENT_STATUS_PENDING,
                new_status=Payment.PAYMENT_STATUS_REFUNDED,
            )

    @patch("ech.payments.services.payment_status_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_status_service.PaymentLogService.log_processing_started")
    def test_change_status_to_processing_updates_payment_order_lifecycle_and_logs(
        self,
        mock_log,
        mock_dispatch,
    ):
        """Ensure processing transition updates payment, lifecycle, order, log, and event."""
        payment = PaymentStatusService.change_status(
            payment=self.payment,
            new_status=Payment.PAYMENT_STATUS_PROCESSING,
            performed_by=self.actor,
            metadata={"source": "test"},
        )

        payment.refresh_from_db()
        self.order.refresh_from_db()
        self.lifecycle.refresh_from_db()

        self.assertEqual(payment.status, Payment.PAYMENT_STATUS_PROCESSING)
        self.assertEqual(self.order.payment_status, Payment.PAYMENT_STATUS_PROCESSING)
        self.assertIsNotNone(self.lifecycle.processing_started_at)

        mock_log.assert_called_once()
        mock_dispatch.assert_called_once()

    @patch("ech.payments.services.payment_status_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_status_service.PaymentLogService.log_authorized")
    def test_change_status_to_authorized_updates_lifecycle_and_logs(
        self,
        mock_log,
        mock_dispatch,
    ):
        """Ensure authorized transition updates lifecycle and dispatches event."""
        self.payment.status = Payment.PAYMENT_STATUS_PROCESSING
        self.payment.save(update_fields=["status"])

        payment = PaymentStatusService.change_status(
            payment=self.payment,
            new_status=Payment.PAYMENT_STATUS_AUTHORIZED,
            performed_by=self.actor,
            metadata={"transaction_id": "tx-123"},
        )

        payment.refresh_from_db()
        self.lifecycle.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(payment.status, Payment.PAYMENT_STATUS_AUTHORIZED)
        self.assertEqual(self.order.payment_status, Payment.PAYMENT_STATUS_AUTHORIZED)
        self.assertIsNotNone(self.lifecycle.authorized_at)

        mock_log.assert_called_once()
        mock_dispatch.assert_called_once()

    @patch("ech.payments.services.payment_status_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_status_service.PaymentLogService.log_captured")
    def test_change_status_to_captured_updates_lifecycle_and_logs(
        self,
        mock_log,
        mock_dispatch,
    ):
        """Ensure captured transition updates lifecycle and dispatches event."""
        self.payment.status = Payment.PAYMENT_STATUS_AUTHORIZED
        self.payment.save(update_fields=["status"])

        payment = PaymentStatusService.change_status(
            payment=self.payment,
            new_status=Payment.PAYMENT_STATUS_CAPTURED,
            performed_by=self.actor,
            metadata={"transaction_id": "tx-456"},
        )

        payment.refresh_from_db()
        self.lifecycle.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(payment.status, Payment.PAYMENT_STATUS_CAPTURED)
        self.assertEqual(self.order.payment_status, Payment.PAYMENT_STATUS_CAPTURED)
        self.assertIsNotNone(self.lifecycle.captured_at)

        mock_log.assert_called_once()
        mock_dispatch.assert_called_once()

    @patch("ech.payments.services.payment_status_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_status_service.PaymentLogService.log_failed")
    def test_change_status_to_failed_updates_lifecycle_and_logs(
        self,
        mock_log,
        mock_dispatch,
    ):
        """Ensure failed transition updates lifecycle and dispatches event."""
        payment = PaymentStatusService.change_status(
            payment=self.payment,
            new_status=Payment.PAYMENT_STATUS_FAILED,
            performed_by=self.actor,
            metadata={
                "transaction_id": "tx-fail",
                "failure_code": "DECLINED",
                "failure_message": "Card declined",
            },
        )

        payment.refresh_from_db()
        self.lifecycle.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(payment.status, Payment.PAYMENT_STATUS_FAILED)
        self.assertEqual(self.order.payment_status, Payment.PAYMENT_STATUS_FAILED)
        self.assertIsNotNone(self.lifecycle.failed_at)

        mock_log.assert_called_once()
        mock_dispatch.assert_called_once()

    @patch("ech.payments.services.payment_status_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_status_service.PaymentLogService.log_cancelled")
    def test_change_status_to_cancelled_updates_lifecycle_and_logs(
        self,
        mock_log,
        mock_dispatch,
    ):
        """Ensure cancelled transition updates lifecycle and dispatches event."""
        payment = PaymentStatusService.change_status(
            payment=self.payment,
            new_status=Payment.PAYMENT_STATUS_CANCELLED,
            performed_by=self.actor,
            metadata={"transaction_id": "tx-cancel"},
        )

        payment.refresh_from_db()
        self.lifecycle.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(payment.status, Payment.PAYMENT_STATUS_CANCELLED)
        self.assertEqual(self.order.payment_status, Payment.PAYMENT_STATUS_CANCELLED)
        self.assertIsNotNone(self.lifecycle.cancelled_at)

        mock_log.assert_called_once()
        mock_dispatch.assert_called_once()

    @patch("ech.payments.services.payment_status_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_status_service.PaymentLogService.log_partially_refunded")
    def test_change_status_to_partially_refunded_updates_lifecycle_and_logs(
        self,
        mock_log,
        mock_dispatch,
    ):
        """Ensure partially refunded transition updates lifecycle and dispatches event."""
        self.payment.status = Payment.PAYMENT_STATUS_CAPTURED
        self.payment.save(update_fields=["status"])

        payment = PaymentStatusService.change_status(
            payment=self.payment,
            new_status=Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
            performed_by=self.actor,
            metadata={
                "refund_id": "refund-1",
                "transaction_id": "tx-refund-1",
                "amount": "20.00",
                "refunded_amount": "20.00",
            },
        )

        payment.refresh_from_db()
        self.lifecycle.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(payment.status, Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED)
        self.assertEqual(
            self.order.payment_status,
            Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
        )
        self.assertIsNotNone(self.lifecycle.partially_refunded_at)

        mock_log.assert_called_once()
        mock_dispatch.assert_called_once()

    @patch("ech.payments.services.payment_status_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_status_service.PaymentLogService.log_refunded")
    def test_change_status_to_refunded_updates_payment_and_order_lifecycles(
        self,
        mock_log,
        mock_dispatch,
    ):
        """Ensure refunded transition updates payment lifecycle, order status, and order lifecycle."""
        self.payment.status = Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED
        self.payment.save(update_fields=["status"])

        order_lifecycle = OrderLifecycle.objects.create(order=self.order)

        payment = PaymentStatusService.change_status(
            payment=self.payment,
            new_status=Payment.PAYMENT_STATUS_REFUNDED,
            performed_by=self.actor,
            metadata={
                "refund_id": "refund-2",
                "transaction_id": "tx-refund-2",
                "amount": "80.00",
                "refunded_amount": "100.00",
            },
        )

        payment.refresh_from_db()
        self.lifecycle.refresh_from_db()
        self.order.refresh_from_db()
        order_lifecycle.refresh_from_db()

        self.assertEqual(payment.status, Payment.PAYMENT_STATUS_REFUNDED)
        self.assertEqual(self.order.payment_status, Payment.PAYMENT_STATUS_REFUNDED)
        self.assertIsNotNone(self.lifecycle.refunded_at)
        self.assertIsNotNone(order_lifecycle.refunded_at)

        mock_log.assert_called_once()
        mock_dispatch.assert_called_once()

    @patch("ech.payments.services.payment_status_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_status_service.PaymentLogService.log_refunded")
    def test_change_status_to_refunded_does_not_override_existing_order_refunded_at(
        self,
        mock_log,
        mock_dispatch,
    ):
        """Ensure refunded transition preserves existing order lifecycle refunded timestamp."""
        self.payment.status = Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED
        self.payment.save(update_fields=["status"])

        order_lifecycle = OrderLifecycle.objects.create(order=self.order)
        existing_refunded_at = order_lifecycle.refunded_at
        if existing_refunded_at is None:
            from django.utils import timezone
            existing_refunded_at = timezone.now()
            order_lifecycle.refunded_at = existing_refunded_at
            order_lifecycle.save(update_fields=["refunded_at", "updated_at"])

        PaymentStatusService.change_status(
            payment=self.payment,
            new_status=Payment.PAYMENT_STATUS_REFUNDED,
            performed_by=self.actor,
            metadata={"refund_id": "refund-3"},
        )

        order_lifecycle.refresh_from_db()
        self.assertEqual(order_lifecycle.refunded_at, existing_refunded_at)

        mock_log.assert_called_once()
        mock_dispatch.assert_called_once()

    def test_update_lifecycle_sets_processing_started_at_only_once(self):
        """Ensure lifecycle processing timestamp is not overwritten once set."""
        PaymentStatusService._update_lifecycle(
            payment=self.payment,
            new_status=Payment.PAYMENT_STATUS_PROCESSING,
        )
        self.lifecycle.refresh_from_db()
        first_value = self.lifecycle.processing_started_at

        PaymentStatusService._update_lifecycle(
            payment=self.payment,
            new_status=Payment.PAYMENT_STATUS_PROCESSING,
        )
        self.lifecycle.refresh_from_db()

        self.assertEqual(self.lifecycle.processing_started_at, first_value)

    def test_sync_order_updates_order_payment_status(self):
        """Ensure order payment status is synchronized from payment status."""
        self.payment.status = Payment.PAYMENT_STATUS_CAPTURED
        self.payment.save(update_fields=["status"])

        PaymentStatusService._sync_order(payment=self.payment)
        self.order.refresh_from_db()

        self.assertEqual(self.order.payment_status, Payment.PAYMENT_STATUS_CAPTURED)

    def test_sync_order_refunded_without_order_lifecycle_does_not_fail(self):
        """Ensure refunded order sync works even when order lifecycle does not exist."""
        self.payment.status = Payment.PAYMENT_STATUS_REFUNDED
        self.payment.save(update_fields=["status"])

        PaymentStatusService._sync_order(payment=self.payment)
        self.order.refresh_from_db()

        self.assertEqual(self.order.payment_status, Payment.PAYMENT_STATUS_REFUNDED)

    @patch("ech.payments.services.payment_status_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_status_service.PaymentLogService.log_processing_started")
    def test_log_event_for_processing_includes_metadata(
        self,
        mock_log,
        mock_dispatch,
    ):
        """Ensure processing log event is dispatched with provided metadata."""
        metadata = {"source": "api"}

        PaymentStatusService._log_event(
            payment=self.payment,
            previous_status=Payment.PAYMENT_STATUS_PENDING,
            new_status=Payment.PAYMENT_STATUS_PROCESSING,
            performed_by=self.actor,
            metadata=metadata,
        )

        mock_log.assert_called_once_with(
            payment=self.payment,
            performed_by=self.actor,
            metadata=metadata,
        )
        mock_dispatch.assert_called_once()

    @patch("ech.payments.services.payment_status_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_status_service.PaymentLogService.log_refunded")
    def test_log_event_for_refunded_without_metadata_still_dispatches(
        self,
        mock_log,
        mock_dispatch,
    ):
        """Ensure refunded log event works even when metadata is not provided."""
        PaymentStatusService._log_event(
            payment=self.payment,
            previous_status=Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
            new_status=Payment.PAYMENT_STATUS_REFUNDED,
            performed_by=self.actor,
            metadata=None,
        )

        mock_log.assert_called_once_with(
            payment=self.payment,
            performed_by=self.actor,
            metadata=None,
        )
        mock_dispatch.assert_called_once()

    def test_change_status_raises_for_invalid_transition(self):
        """Ensure change_status raises for disallowed transition."""
        with self.assertRaises(InvalidPaymentStatusTransition):
            PaymentStatusService.change_status(
                payment=self.payment,
                new_status=Payment.PAYMENT_STATUS_REFUNDED,
                performed_by=self.actor,
            )