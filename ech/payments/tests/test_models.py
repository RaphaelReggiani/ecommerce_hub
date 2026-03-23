from decimal import Decimal
import uuid

from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.utils import timezone

from ech.orders.models import Order
from ech.payments.models import (
    Payment,
    PaymentEvent,
    PaymentLifecycle,
    PaymentRefund,
    PaymentTransaction,
)
from ech.users.models import CustomUser


class PaymentModelsTestCase(TestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.actor = CustomUser.objects.create_user(
            email="actor@test.com",
            password="StrongPassword123",
            user_name="Actor User",
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
            method=Payment.PAYMENT_METHOD_CREDIT_CARD,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("150.00"),
        )

    def test_payment_creation_with_required_fields(self):
        """Ensure Payment is created correctly with required fields."""
        self.assertIsInstance(self.payment.id, uuid.UUID)
        self.assertEqual(self.payment.order, self.order)
        self.assertEqual(self.payment.customer, self.customer)
        self.assertEqual(self.payment.payment_reference, "PAY-001")
        self.assertEqual(self.payment.method, Payment.PAYMENT_METHOD_CREDIT_CARD)
        self.assertEqual(self.payment.status, Payment.PAYMENT_STATUS_PENDING)
        self.assertEqual(self.payment.amount, Decimal("150.00"))

    def test_payment_defaults_are_applied(self):
        """Ensure Payment default values are applied on creation."""
        self.assertEqual(self.payment.refunded_amount, 0)
        self.assertEqual(self.payment.currency, "USD")
        self.assertEqual(self.payment.gateway_name, "")
        self.assertEqual(self.payment.gateway_payment_id, "")
        self.assertEqual(self.payment.gateway_customer_id, "")
        self.assertEqual(self.payment.failure_code, "")
        self.assertEqual(self.payment.failure_message, "")
        self.assertIsNone(self.payment.idempotency_key)
        self.assertIsNone(self.payment.metadata)
        self.assertIsNotNone(self.payment.created_at)
        self.assertIsNotNone(self.payment.updated_at)

    def test_payment_string_representation(self):
        """Ensure Payment string representation uses payment reference."""
        self.assertEqual(str(self.payment), "Payment PAY-001")

    def test_payment_ordering_by_created_at_desc(self):
        """Ensure Payment objects are ordered by newest first."""
        older_payment = Payment.objects.create(
            order=Order.objects.create(
                customer=self.customer,
                status=Order.ORDER_STATUS_PENDING,
                payment_status=Order.PAYMENT_STATUS_PENDING,
                shipping_status=Order.SHIPPING_STATUS_PENDING,
            ),
            customer=self.customer,
            payment_reference="PAY-OLD",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("50.00"),
        )

        newer_payment = Payment.objects.create(
            order=Order.objects.create(
                customer=self.customer,
                status=Order.ORDER_STATUS_PENDING,
                payment_status=Order.PAYMENT_STATUS_PENDING,
                shipping_status=Order.SHIPPING_STATUS_PENDING,
            ),
            customer=self.customer,
            payment_reference="PAY-NEW",
            method=Payment.PAYMENT_METHOD_DEBIT_CARD,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("75.00"),
        )

        older_time = timezone.now() - timezone.timedelta(days=1)
        Payment.objects.filter(id=older_payment.id).update(created_at=older_time)

        payments = list(Payment.objects.all())
        self.assertEqual(payments[0].id, newer_payment.id)
        self.assertEqual(payments[-1].id, older_payment.id)

    def test_payment_reference_must_be_unique(self):
        """Ensure Payment reference cannot be duplicated."""
        with self.assertRaises(IntegrityError):
            Payment.objects.create(
                order=Order.objects.create(
                    customer=self.customer,
                    status=Order.ORDER_STATUS_PENDING,
                    payment_status=Order.PAYMENT_STATUS_PENDING,
                    shipping_status=Order.SHIPPING_STATUS_PENDING,
                ),
                customer=self.customer,
                payment_reference="PAY-001",
                method=Payment.PAYMENT_METHOD_CREDIT_CARD,
                status=Payment.PAYMENT_STATUS_PENDING,
                amount=Decimal("99.00"),
            )

    def test_payment_idempotency_key_must_be_unique_when_present(self):
        """Ensure Payment idempotency key is unique when provided."""
        idempotency_key = uuid.uuid4()

        Payment.objects.create(
            order=Order.objects.create(
                customer=self.customer,
                status=Order.ORDER_STATUS_PENDING,
                payment_status=Order.PAYMENT_STATUS_PENDING,
                shipping_status=Order.SHIPPING_STATUS_PENDING,
            ),
            customer=self.customer,
            payment_reference="PAY-IDEMP-1",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("10.00"),
            idempotency_key=idempotency_key,
        )

        with self.assertRaises(IntegrityError):
            Payment.objects.create(
                order=Order.objects.create(
                    customer=self.customer,
                    status=Order.ORDER_STATUS_PENDING,
                    payment_status=Order.PAYMENT_STATUS_PENDING,
                    shipping_status=Order.SHIPPING_STATUS_PENDING,
                ),
                customer=self.customer,
                payment_reference="PAY-IDEMP-2",
                method=Payment.PAYMENT_METHOD_PIX,
                status=Payment.PAYMENT_STATUS_PENDING,
                amount=Decimal("20.00"),
                idempotency_key=idempotency_key,
            )

    def test_payment_allows_null_idempotency_key_for_multiple_records(self):
        """Ensure multiple Payment records allow null idempotency keys."""
        payment_2 = Payment.objects.create(
            order=Order.objects.create(
                customer=self.customer,
                status=Order.ORDER_STATUS_PENDING,
                payment_status=Order.PAYMENT_STATUS_PENDING,
                shipping_status=Order.SHIPPING_STATUS_PENDING,
            ),
            customer=self.customer,
            payment_reference="PAY-NULL-IDEMP",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("30.00"),
            idempotency_key=None,
        )

        self.assertIsNone(self.payment.idempotency_key)
        self.assertIsNone(payment_2.idempotency_key)

    def test_payment_deleting_order_is_protected(self):
        """Ensure deleting an Order with Payment raises ProtectedError."""
        with self.assertRaises(ProtectedError):
            self.order.delete()

    def test_payment_deleting_customer_is_protected(self):
        """Ensure deleting a Customer with Payment raises ProtectedError."""
        with self.assertRaises(ProtectedError):
            self.customer.delete()

    def test_payment_transaction_creation_and_string_representation(self):
        """Ensure PaymentTransaction is created and stringified correctly."""
        transaction = PaymentTransaction.objects.create(
            payment=self.payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=Decimal("150.00"),
            performed_by=self.actor,
        )

        self.assertIsInstance(transaction.id, uuid.UUID)
        self.assertEqual(transaction.payment, self.payment)
        self.assertEqual(
            transaction.transaction_type,
            PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION,
        )
        self.assertEqual(
            transaction.status,
            PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
        )
        self.assertEqual(transaction.currency, "USD")
        self.assertEqual(str(transaction), "authorization - PAY-001")

    def test_payment_transaction_ordering_by_created_at_desc(self):
        """Ensure PaymentTransaction objects are ordered by newest first."""
        older_transaction = PaymentTransaction.objects.create(
            payment=self.payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION,
            status=PaymentTransaction.TRANSACTION_STATUS_PENDING,
            amount=Decimal("50.00"),
            performed_by=self.actor,
        )

        newer_transaction = PaymentTransaction.objects.create(
            payment=self.payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_CAPTURE,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=Decimal("50.00"),
            performed_by=self.actor,
        )

        older_time = timezone.now() - timezone.timedelta(days=1)
        PaymentTransaction.objects.filter(id=older_transaction.id).update(
            created_at=older_time
        )

        transactions = list(PaymentTransaction.objects.all())
        self.assertEqual(transactions[0].id, newer_transaction.id)
        self.assertEqual(transactions[-1].id, older_transaction.id)

    def test_payment_transaction_idempotency_key_must_be_unique_when_present(self):
        """Ensure PaymentTransaction idempotency key is unique when provided."""
        idempotency_key = uuid.uuid4()

        PaymentTransaction.objects.create(
            payment=self.payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=Decimal("10.00"),
            idempotency_key=idempotency_key,
        )

        with self.assertRaises(IntegrityError):
            PaymentTransaction.objects.create(
                payment=self.payment,
                transaction_type=PaymentTransaction.TRANSACTION_TYPE_CAPTURE,
                status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
                amount=Decimal("10.00"),
                idempotency_key=idempotency_key,
            )

    def test_payment_transaction_performed_by_is_set_null_when_user_is_deleted(self):
        """Ensure PaymentTransaction performer becomes null after user deletion."""
        transaction = PaymentTransaction.objects.create(
            payment=self.payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_CAPTURE,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=Decimal("150.00"),
            performed_by=self.actor,
        )

        self.actor.delete()
        transaction.refresh_from_db()

        self.assertIsNone(transaction.performed_by)

    def test_payment_refund_creation_and_string_representation(self):
        """Ensure PaymentRefund is created and stringified correctly."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("25.00"),
            reason="Customer request",
            status=PaymentRefund.REFUND_STATUS_PENDING,
            requested_by=self.actor,
            processed_by=self.actor,
        )

        self.assertIsInstance(refund.id, uuid.UUID)
        self.assertEqual(refund.payment, self.payment)
        self.assertEqual(refund.amount, Decimal("25.00"))
        self.assertEqual(refund.reason, "Customer request")
        self.assertEqual(refund.status, PaymentRefund.REFUND_STATUS_PENDING)
        self.assertEqual(str(refund), f"Refund {refund.id} - PAY-001")

    def test_payment_refund_ordering_by_created_at_desc(self):
        """Ensure PaymentRefund objects are ordered by newest first."""
        older_refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("10.00"),
            reason="Older refund",
            status=PaymentRefund.REFUND_STATUS_PENDING,
            requested_by=self.actor,
        )

        newer_refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("20.00"),
            reason="Newer refund",
            status=PaymentRefund.REFUND_STATUS_PROCESSED,
            requested_by=self.actor,
        )

        older_time = timezone.now() - timezone.timedelta(days=1)
        PaymentRefund.objects.filter(id=older_refund.id).update(created_at=older_time)

        refunds = list(PaymentRefund.objects.all())
        self.assertEqual(refunds[0].id, newer_refund.id)
        self.assertEqual(refunds[-1].id, older_refund.id)

    def test_payment_refund_requested_by_is_set_null_when_user_is_deleted(self):
        """Ensure refund requester becomes null after user deletion."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("35.00"),
            reason="Requested only",
            status=PaymentRefund.REFUND_STATUS_PENDING,
            requested_by=self.actor,
        )

        self.actor.delete()
        refund.refresh_from_db()

        self.assertIsNone(refund.requested_by)

    def test_payment_refund_processed_by_is_set_null_when_user_is_deleted(self):
        """Ensure refund processor becomes null after user deletion."""
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("35.00"),
            reason="Processed only",
            status=PaymentRefund.REFUND_STATUS_PROCESSED,
            processed_by=self.actor,
        )

        self.actor.delete()
        refund.refresh_from_db()

        self.assertIsNone(refund.processed_by)

    def test_payment_lifecycle_creation_and_string_representation(self):
        """Ensure PaymentLifecycle is created and stringified correctly."""
        lifecycle = PaymentLifecycle.objects.create(payment=self.payment)

        self.assertEqual(lifecycle.payment, self.payment)
        self.assertEqual(str(lifecycle), f"Lifecycle for Payment {self.payment.id}")

    def test_payment_lifecycle_must_be_one_to_one_with_payment(self):
        """Ensure only one lifecycle can exist per Payment."""
        PaymentLifecycle.objects.create(payment=self.payment)

        with self.assertRaises(IntegrityError):
            PaymentLifecycle.objects.create(payment=self.payment)

    def test_payment_event_creation_and_string_representation(self):
        """Ensure PaymentEvent is created and stringified correctly."""
        event = PaymentEvent.objects.create(
            payment=self.payment,
            event_type=PaymentEvent.TYPE_CREATED,
            performed_by=self.actor,
            metadata={"source": "test"},
        )

        self.assertIsInstance(event.id, uuid.UUID)
        self.assertEqual(event.payment, self.payment)
        self.assertEqual(event.event_type, PaymentEvent.TYPE_CREATED)
        self.assertEqual(event.metadata, {"source": "test"})
        self.assertEqual(str(event), "created - PAY-001")

    def test_payment_event_ordering_by_created_at_desc(self):
        """Ensure PaymentEvent objects are ordered by newest first."""
        older_event = PaymentEvent.objects.create(
            payment=self.payment,
            event_type=PaymentEvent.TYPE_CREATED,
            performed_by=self.actor,
        )

        newer_event = PaymentEvent.objects.create(
            payment=self.payment,
            event_type=PaymentEvent.TYPE_CAPTURED,
            performed_by=self.actor,
        )

        older_time = timezone.now() - timezone.timedelta(days=1)
        PaymentEvent.objects.filter(id=older_event.id).update(created_at=older_time)

        events = list(PaymentEvent.objects.all())
        self.assertEqual(events[0].id, newer_event.id)
        self.assertEqual(events[-1].id, older_event.id)

    def test_payment_event_performed_by_is_set_null_when_user_is_deleted(self):
        """Ensure event performer becomes null after user deletion."""
        event = PaymentEvent.objects.create(
            payment=self.payment,
            event_type=PaymentEvent.TYPE_CREATED,
            performed_by=self.actor,
        )

        self.actor.delete()
        event.refresh_from_db()

        self.assertIsNone(event.performed_by)

    def test_deleting_payment_cascades_to_transactions_refunds_lifecycle_and_events(self):
        """Ensure deleting Payment cascades to all dependent payment records."""
        transaction = PaymentTransaction.objects.create(
            payment=self.payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=Decimal("150.00"),
        )

        refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("20.00"),
            reason="Cascade check",
            status=PaymentRefund.REFUND_STATUS_PENDING,
        )

        PaymentLifecycle.objects.create(payment=self.payment)

        event = PaymentEvent.objects.create(
            payment=self.payment,
            event_type=PaymentEvent.TYPE_CREATED,
        )

        payment_id = self.payment.id
        transaction_id = transaction.id
        refund_id = refund.id
        event_id = event.id

        self.payment.delete()

        self.assertFalse(Payment.objects.filter(id=payment_id).exists())
        self.assertFalse(PaymentTransaction.objects.filter(id=transaction_id).exists())
        self.assertFalse(PaymentRefund.objects.filter(id=refund_id).exists())
        self.assertFalse(PaymentLifecycle.objects.filter(payment_id=payment_id).exists())
        self.assertFalse(PaymentEvent.objects.filter(id=event_id).exists())