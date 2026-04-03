from decimal import Decimal
import uuid

from django.test import TestCase

from ech.orders.models import Order, OrderTotals
from ech.payments.models import Payment, PaymentEvent
from ech.payments.services.payment_log_service import PaymentLogService
from ech.users.models import CustomUser


class PaymentLogServiceTestCase(TestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            email="customer_log@test.com",
            password="StrongPassword123",
            user_name="Customer Log",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.actor = CustomUser.objects.create_user(
            email="actor_log@test.com",
            password="StrongPassword123",
            user_name="Actor Log",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.order = Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

        OrderTotals.objects.create(
            order=self.order,
            subtotal=Decimal("100.00"),
            discount_total=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            shipping_total=Decimal("0.00"),
            grand_total=Decimal("100.00"),
        )

        self.payment = Payment.objects.create(
            order=self.order,
            customer=self.customer,
            payment_reference=f"PAY-LOG-{uuid.uuid4().hex[:8].upper()}",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("100.00"),
            refunded_amount=Decimal("0.00"),
            currency="USD",
        )

    def test_log_event_creates_payment_event_with_expected_fields(self):
        metadata = {"gateway": "stripe", "attempt": 1}

        event = PaymentLogService.log_event(
            payment=self.payment,
            event_type=PaymentEvent.TYPE_CREATED,
            performed_by=self.actor,
            metadata=metadata,
        )

        self.assertIsInstance(event, PaymentEvent)
        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.event_type, PaymentEvent.TYPE_CREATED)
        self.assertEqual(event.performed_by, self.actor)
        self.assertEqual(event.metadata, metadata)

    def test_log_event_uses_empty_metadata_when_none_is_provided(self):
        event = PaymentLogService.log_event(
            payment=self.payment,
            event_type=PaymentEvent.TYPE_CREATED,
        )

        self.assertEqual(event.metadata, {})

    def test_log_created_registers_created_event(self):
        event = PaymentLogService.log_created(
            payment=self.payment,
            performed_by=self.actor,
            metadata={"source": "api"},
        )

        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.event_type, PaymentEvent.TYPE_CREATED)
        self.assertEqual(event.performed_by, self.actor)
        self.assertEqual(event.metadata, {"source": "api"})

    def test_log_processing_started_registers_processing_started_event(self):
        event = PaymentLogService.log_processing_started(
            payment=self.payment,
            performed_by=self.actor,
            metadata={"step": "start_processing"},
        )

        self.assertEqual(event.event_type, PaymentEvent.TYPE_PROCESSING_STARTED)
        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.performed_by, self.actor)
        self.assertEqual(event.metadata, {"step": "start_processing"})

    def test_log_authorized_registers_authorized_event(self):
        event = PaymentLogService.log_authorized(
            payment=self.payment,
            performed_by=self.actor,
            metadata={"gateway_status": "authorized"},
        )

        self.assertEqual(event.event_type, PaymentEvent.TYPE_AUTHORIZED)
        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.performed_by, self.actor)
        self.assertEqual(event.metadata, {"gateway_status": "authorized"})

    def test_log_captured_registers_captured_event(self):
        event = PaymentLogService.log_captured(
            payment=self.payment,
            performed_by=self.actor,
            metadata={"captured_amount": "100.00"},
        )

        self.assertEqual(event.event_type, PaymentEvent.TYPE_CAPTURED)
        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.performed_by, self.actor)
        self.assertEqual(event.metadata, {"captured_amount": "100.00"})

    def test_log_failed_registers_failed_event(self):
        event = PaymentLogService.log_failed(
            payment=self.payment,
            performed_by=self.actor,
            metadata={"reason": "gateway_error"},
        )

        self.assertEqual(event.event_type, PaymentEvent.TYPE_FAILED)
        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.performed_by, self.actor)
        self.assertEqual(event.metadata, {"reason": "gateway_error"})

    def test_log_cancelled_registers_cancelled_event(self):
        event = PaymentLogService.log_cancelled(
            payment=self.payment,
            performed_by=self.actor,
            metadata={"reason": "manual_cancellation"},
        )

        self.assertEqual(event.event_type, PaymentEvent.TYPE_CANCELLED)
        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.performed_by, self.actor)
        self.assertEqual(event.metadata, {"reason": "manual_cancellation"})

    def test_log_refund_requested_registers_refund_requested_event(self):
        event = PaymentLogService.log_refund_requested(
            payment=self.payment,
            performed_by=self.actor,
            metadata={"refund_amount": "25.00"},
        )

        self.assertEqual(event.event_type, PaymentEvent.TYPE_REFUND_REQUESTED)
        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.performed_by, self.actor)
        self.assertEqual(event.metadata, {"refund_amount": "25.00"})

    def test_log_partially_refunded_registers_partially_refunded_event(self):
        event = PaymentLogService.log_partially_refunded(
            payment=self.payment,
            performed_by=self.actor,
            metadata={"refunded_amount": "25.00"},
        )

        self.assertEqual(event.event_type, PaymentEvent.TYPE_PARTIALLY_REFUNDED)
        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.performed_by, self.actor)
        self.assertEqual(event.metadata, {"refunded_amount": "25.00"})

    def test_log_refunded_registers_refunded_event(self):
        event = PaymentLogService.log_refunded(
            payment=self.payment,
            performed_by=self.actor,
            metadata={"refunded_amount": "100.00"},
        )

        self.assertEqual(event.event_type, PaymentEvent.TYPE_REFUNDED)
        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.performed_by, self.actor)
        self.assertEqual(event.metadata, {"refunded_amount": "100.00"})

    def test_log_refund_failed_registers_refund_failed_event(self):
        event = PaymentLogService.log_refund_failed(
            payment=self.payment,
            performed_by=self.actor,
            metadata={"reason": "refund_gateway_error"},
        )

        self.assertEqual(event.event_type, PaymentEvent.TYPE_REFUND_FAILED)
        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.performed_by, self.actor)
        self.assertEqual(event.metadata, {"reason": "refund_gateway_error"})

    def test_log_refund_cancelled_registers_refund_cancelled_event(self):
        event = PaymentLogService.log_refund_cancelled(
            payment=self.payment,
            performed_by=self.actor,
            metadata={"reason": "refund_request_cancelled"},
        )

        self.assertEqual(event.event_type, PaymentEvent.TYPE_REFUND_CANCELLED)
        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.performed_by, self.actor)
        self.assertEqual(event.metadata, {"reason": "refund_request_cancelled"})

    def test_multiple_log_calls_create_multiple_persistent_events(self):
        PaymentLogService.log_created(payment=self.payment)
        PaymentLogService.log_processing_started(payment=self.payment)
        PaymentLogService.log_authorized(payment=self.payment)

        events = PaymentEvent.objects.filter(payment=self.payment).order_by("created_at")

        self.assertEqual(events.count(), 3)
        self.assertEqual(events[0].event_type, PaymentEvent.TYPE_CREATED)
        self.assertEqual(events[1].event_type, PaymentEvent.TYPE_PROCESSING_STARTED)
        self.assertEqual(events[2].event_type, PaymentEvent.TYPE_AUTHORIZED)