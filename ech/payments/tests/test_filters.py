from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from ech.orders.models import Order
from ech.payments.filters import PaymentFilter
from ech.payments.models import Payment
from ech.users.models import CustomUser


class PaymentFilterTestCase(TestCase):
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

        self.order_1 = Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        self.order_2 = Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        self.order_3 = Order.objects.create(
            customer=self.other_customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        self.payment_1 = Payment.objects.create(
            order=self.order_1,
            customer=self.customer,
            payment_reference="PAY-PIX-001",
            gateway_payment_id="gw_pix_abc123",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("100.00"),
            refunded_amount=Decimal("0.00"),
        )

        self.payment_2 = Payment.objects.create(
            order=self.order_2,
            customer=self.customer,
            payment_reference="PAY-CARD-002",
            gateway_payment_id="gw_card_def456",
            method=Payment.PAYMENT_METHOD_CREDIT_CARD,
            status=Payment.PAYMENT_STATUS_CAPTURED,
            amount=Decimal("200.00"),
            refunded_amount=Decimal("50.00"),
        )

        self.payment_3 = Payment.objects.create(
            order=self.order_3,
            customer=self.other_customer,
            payment_reference="PAY-WALLET-003",
            gateway_payment_id="gw_wallet_xyz789",
            method=Payment.PAYMENT_METHOD_WALLET,
            status=Payment.PAYMENT_STATUS_REFUNDED,
            amount=Decimal("300.00"),
            refunded_amount=Decimal("300.00"),
        )

        now = timezone.now()
        Payment.objects.filter(id=self.payment_1.id).update(created_at=now - timedelta(days=3))
        Payment.objects.filter(id=self.payment_2.id).update(created_at=now - timedelta(days=2))
        Payment.objects.filter(id=self.payment_3.id).update(created_at=now - timedelta(days=1))

        self.payment_1.refresh_from_db()
        self.payment_2.refresh_from_db()
        self.payment_3.refresh_from_db()

    def test_filter_by_status(self):
        """Ensure filter returns payments matching the given status."""
        filtered = PaymentFilter(
            data={"status": Payment.PAYMENT_STATUS_PENDING},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(list(filtered), [self.payment_1])

    def test_filter_by_method(self):
        """Ensure filter returns payments matching the given method."""
        filtered = PaymentFilter(
            data={"method": Payment.PAYMENT_METHOD_CREDIT_CARD},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(list(filtered), [self.payment_2])

    def test_filter_by_customer_id(self):
        """Ensure filter returns payments belonging to the informed customer."""
        filtered = PaymentFilter(
            data={"customer_id": str(self.customer.id)},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(set(filtered), {self.payment_1, self.payment_2})

    def test_filter_by_order_id(self):
        """Ensure filter returns payment belonging to the informed order."""
        filtered = PaymentFilter(
            data={"order_id": str(self.order_3.id)},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(list(filtered), [self.payment_3])

    def test_filter_by_payment_reference_icontains(self):
        """Ensure filter performs case-insensitive partial search by payment reference."""
        filtered = PaymentFilter(
            data={"payment_reference": "card"},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(list(filtered), [self.payment_2])

    def test_filter_by_gateway_payment_id_icontains(self):
        """Ensure filter performs case-insensitive partial search by gateway payment id."""
        filtered = PaymentFilter(
            data={"gateway_payment_id": "wallet"},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(list(filtered), [self.payment_3])

    def test_filter_by_min_amount(self):
        """Ensure filter returns payments with amount greater than or equal to min_amount."""
        filtered = PaymentFilter(
            data={"min_amount": "200"},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(set(filtered), {self.payment_2, self.payment_3})

    def test_filter_by_max_amount(self):
        """Ensure filter returns payments with amount less than or equal to max_amount."""
        filtered = PaymentFilter(
            data={"max_amount": "200"},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(set(filtered), {self.payment_1, self.payment_2})

    def test_filter_by_min_refunded_amount(self):
        """Ensure filter returns payments with refunded amount greater than or equal to the minimum."""
        filtered = PaymentFilter(
            data={"min_refunded_amount": "50"},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(set(filtered), {self.payment_2, self.payment_3})

    def test_filter_by_max_refunded_amount(self):
        """Ensure filter returns payments with refunded amount less than or equal to the maximum."""
        filtered = PaymentFilter(
            data={"max_refunded_amount": "50"},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(set(filtered), {self.payment_1, self.payment_2})

    def test_filter_by_created_after(self):
        """Ensure filter returns payments created on or after the given datetime."""
        cutoff = self.payment_2.created_at.isoformat()

        filtered = PaymentFilter(
            data={"created_after": cutoff},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(set(filtered), {self.payment_2, self.payment_3})

    def test_filter_by_created_before(self):
        """Ensure filter returns payments created on or before the given datetime."""
        cutoff = self.payment_2.created_at.isoformat()

        filtered = PaymentFilter(
            data={"created_before": cutoff},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(set(filtered), {self.payment_1, self.payment_2})

    def test_filter_is_refunded_true(self):
        """Ensure filter returns fully refunded payments when is_refunded is true."""
        filtered = PaymentFilter(
            data={"is_refunded": "true"},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(list(filtered), [self.payment_3])

    def test_filter_is_refunded_false(self):
        """Ensure filter excludes fully refunded payments when is_refunded is false."""
        filtered = PaymentFilter(
            data={"is_refunded": "false"},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(set(filtered), {self.payment_1, self.payment_2})

    def test_filter_is_partially_refunded_true(self):
        """Ensure filter returns partially refunded payments when flag is true."""
        filtered = PaymentFilter(
            data={"is_partially_refunded": "true"},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(list(filtered), [self.payment_2])

    def test_filter_is_partially_refunded_false(self):
        """Ensure filter excludes partially refunded payments when flag is false."""
        filtered = PaymentFilter(
            data={"is_partially_refunded": "false"},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(set(filtered), {self.payment_1, self.payment_3})

    def test_filter_combines_multiple_criteria(self):
        """Ensure filter combines multiple criteria correctly."""
        filtered = PaymentFilter(
            data={
                "customer_id": str(self.customer.id),
                "method": Payment.PAYMENT_METHOD_CREDIT_CARD,
                "min_amount": "150",
                "max_amount": "250",
            },
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(list(filtered), [self.payment_2])

    def test_filter_with_no_params_returns_all_payments(self):
        """Ensure filter returns all payments when no parameters are provided."""
        filtered = PaymentFilter(
            data={},
            queryset=Payment.objects.all(),
        ).qs

        self.assertEqual(set(filtered), {self.payment_1, self.payment_2, self.payment_3})