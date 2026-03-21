from decimal import Decimal
import uuid

from django.test import TestCase
from django.utils import timezone

from ech.orders.models import Order
from ech.payments.exceptions import (
    PaymentNotFound,
    PaymentRefundNotFound,
)
from ech.payments.models import (
    Payment,
    PaymentEvent,
    PaymentLifecycle,
    PaymentRefund,
    PaymentTransaction,
)
from ech.payments.selectors import (
    get_payment_by_id,
    get_payment_by_order_id,
    get_payment_by_reference,
    get_payment_for_customer,
    get_payment_lifecycle,
    get_payment_management_detail,
    get_payment_refund_by_id,
    get_payment_with_details,
    list_payment_events,
    list_payment_refunds,
    list_payment_refunds_for_management,
    list_payment_transactions,
    list_payments_by_method,
    list_payments_by_status,
    list_payments_for_customer,
    list_payments_for_management,
    list_pending_payment_refunds,
)
from ech.users.models import CustomUser


class PaymentSelectorsTestCase(TestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.other_customer = CustomUser.objects.create_user(
            email="other@test.com",
            password="StrongPassword123",
            user_name="Other Customer",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        # Para selectors, não precisamos de role de staff.
        # Basta um usuário válido para os campos performed_by/requested_by/processed_by.
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

        self.other_order = Order.objects.create(
            customer=self.other_customer,
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

        self.other_payment = Payment.objects.create(
            order=self.other_order,
            customer=self.other_customer,
            payment_reference="PAY-002",
            method=Payment.PAYMENT_METHOD_CREDIT_CARD,
            status=Payment.PAYMENT_STATUS_CAPTURED,
            amount=Decimal("200.00"),
            refunded_amount=Decimal("50.00"),
        )

        self.lifecycle = PaymentLifecycle.objects.create(payment=self.payment)

        self.transaction = PaymentTransaction.objects.create(
            payment=self.payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=Decimal("100.00"),
            performed_by=self.actor,
        )

        self.refund = PaymentRefund.objects.create(
            payment=self.payment,
            amount=Decimal("20.00"),
            reason="Test refund",
            status=PaymentRefund.REFUND_STATUS_PENDING,
            requested_by=self.actor,
            processed_by=self.actor,
        )

        self.other_refund = PaymentRefund.objects.create(
            payment=self.other_payment,
            amount=Decimal("50.00"),
            reason="Processed refund",
            status=PaymentRefund.REFUND_STATUS_PROCESSED,
            requested_by=self.actor,
            processed_by=self.actor,
        )

        self.event = PaymentEvent.objects.create(
            payment=self.payment,
            event_type=PaymentEvent.TYPE_CREATED,
            performed_by=self.actor,
        )

    def test_get_payment_by_id_returns_payment(self):
        """Ensure selector returns the expected payment by id."""
        result = get_payment_by_id(payment_id=self.payment.id)

        self.assertEqual(result.id, self.payment.id)

    def test_get_payment_by_id_raises_exception_when_missing(self):
        """Ensure selector raises PaymentNotFound for unknown payment id."""
        with self.assertRaises(PaymentNotFound):
            get_payment_by_id(payment_id=uuid.uuid4())

    def test_get_payment_by_reference_returns_payment(self):
        """Ensure selector returns the expected payment by reference."""
        result = get_payment_by_reference(payment_reference="PAY-001")

        self.assertEqual(result.id, self.payment.id)

    def test_get_payment_by_reference_raises_exception_when_missing(self):
        """Ensure selector raises PaymentNotFound for unknown payment reference."""
        with self.assertRaises(PaymentNotFound):
            get_payment_by_reference(payment_reference="INVALID-REF")

    def test_get_payment_with_details_returns_full_payment(self):
        """Ensure selector returns payment with related detail objects available."""
        result = get_payment_with_details(payment_id=self.payment.id)

        self.assertEqual(result.id, self.payment.id)
        self.assertEqual(result.order.id, self.order.id)
        self.assertEqual(result.customer.id, self.customer.id)
        self.assertEqual(result.lifecycle.id, self.lifecycle.id)
        self.assertEqual(result.transactions.count(), 1)
        self.assertEqual(result.refunds.count(), 1)
        self.assertEqual(result.events.count(), 1)

    def test_get_payment_with_details_raises_exception_when_missing(self):
        """Ensure detailed selector raises PaymentNotFound for unknown payment."""
        with self.assertRaises(PaymentNotFound):
            get_payment_with_details(payment_id=uuid.uuid4())

    def test_get_payment_management_detail_returns_payment(self):
        """Ensure management detail selector returns the expected payment."""
        result = get_payment_management_detail(payment_id=self.payment.id)

        self.assertEqual(result.id, self.payment.id)
        self.assertEqual(result.transactions.count(), 1)
        self.assertEqual(result.refunds.count(), 1)
        self.assertEqual(result.events.count(), 1)

    def test_get_payment_for_customer_returns_payment(self):
        """Ensure customer selector returns payment owned by the customer."""
        result = get_payment_for_customer(
            payment_id=self.payment.id,
            customer_id=self.customer.id,
        )

        self.assertEqual(result.id, self.payment.id)

    def test_get_payment_for_customer_blocks_other_users(self):
        """Ensure customer selector hides payments from other customers."""
        with self.assertRaises(PaymentNotFound):
            get_payment_for_customer(
                payment_id=self.payment.id,
                customer_id=self.other_customer.id,
            )

    def test_get_payment_by_order_id_returns_payment(self):
        """Ensure selector returns payment associated with the given order."""
        result = get_payment_by_order_id(order_id=self.order.id)

        self.assertEqual(result.id, self.payment.id)

    def test_get_payment_by_order_id_raises_exception_when_missing(self):
        """Ensure selector raises PaymentNotFound when order has no payment."""
        order_without_payment = Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        with self.assertRaises(PaymentNotFound):
            get_payment_by_order_id(order_id=order_without_payment.id)

    def test_list_payments_for_customer_returns_only_customer_payments(self):
        """Ensure selector returns only payments owned by the informed customer."""
        result = list(list_payments_for_customer(customer_id=self.customer.id))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.payment.id)

    def test_list_payments_for_management_returns_all(self):
        """Ensure management selector returns all payments."""
        result = list(list_payments_for_management())

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, self.other_payment.id)
        self.assertEqual(result[1].id, self.payment.id)

    def test_list_payments_by_status_filters_correctly(self):
        """Ensure selector filters payments by status."""
        result = list(
            list_payments_by_status(status_value=Payment.PAYMENT_STATUS_PENDING)
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.payment.id)

    def test_list_payments_by_method_filters_correctly(self):
        """Ensure selector filters payments by method."""
        result = list(
            list_payments_by_method(method_value=Payment.PAYMENT_METHOD_PIX)
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.payment.id)

    def test_list_payment_transactions_returns_transactions(self):
        """Ensure selector returns transactions for the informed payment."""
        result = list(list_payment_transactions(payment_id=self.payment.id))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.transaction.id)

    def test_list_payment_refunds_returns_refunds(self):
        """Ensure selector returns refunds for the informed payment."""
        result = list(list_payment_refunds(payment_id=self.payment.id))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.refund.id)

    def test_list_payment_events_returns_events(self):
        """Ensure selector returns events for the informed payment."""
        result = list(list_payment_events(payment_id=self.payment.id))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.event.id)

    def test_get_payment_lifecycle_returns_lifecycle(self):
        """Ensure selector returns lifecycle for a payment that has one."""
        result = get_payment_lifecycle(payment_id=self.payment.id)

        self.assertEqual(result.id, self.lifecycle.id)

    def test_get_payment_lifecycle_raises_when_payment_is_missing(self):
        """Ensure selector raises PaymentNotFound for unknown payment lifecycle lookup."""
        with self.assertRaises(PaymentNotFound):
            get_payment_lifecycle(payment_id=uuid.uuid4())

    def test_get_payment_lifecycle_raises_when_lifecycle_is_missing(self):
        """Ensure selector raises PaymentNotFound when payment has no lifecycle."""
        payment_without_lifecycle = Payment.objects.create(
            order=Order.objects.create(
                customer=self.customer,
                status=Order.ORDER_STATUS_PENDING,
                payment_status=Order.PAYMENT_STATUS_PENDING,
                shipping_status=Order.SHIPPING_STATUS_PENDING,
            ),
            customer=self.customer,
            payment_reference="PAY-003",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("75.00"),
        )

        with self.assertRaises(PaymentNotFound):
            get_payment_lifecycle(payment_id=payment_without_lifecycle.id)

    def test_get_payment_refund_by_id_returns_refund(self):
        """Ensure selector returns refund by id."""
        result = get_payment_refund_by_id(refund_id=self.refund.id)

        self.assertEqual(result.id, self.refund.id)

    def test_get_payment_refund_by_id_raises_when_missing(self):
        """Ensure selector raises PaymentRefundNotFound for unknown refund id."""
        with self.assertRaises(PaymentRefundNotFound):
            get_payment_refund_by_id(refund_id=uuid.uuid4())

    def test_list_pending_payment_refunds_returns_only_pending(self):
        """Ensure selector returns only refunds with pending status."""
        result = list(list_pending_payment_refunds())

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.refund.id)

    def test_list_payment_refunds_for_management_returns_all(self):
        """Ensure management selector returns all refunds."""
        result = list(list_payment_refunds_for_management())

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, self.other_refund.id)
        self.assertEqual(result[1].id, self.refund.id)