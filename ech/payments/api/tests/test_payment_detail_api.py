from decimal import Decimal
import uuid

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.orders.models import (
    Order, 
    OrderTotals,
)
from ech.payments.models import Payment
from ech.users.models import CustomUser


class PaymentDetailApiTestCase(APITestCase):

    def setUp(self):
        """Set up common test data for payment detail API tests."""

        cache.clear()

        self.password = "StrongPassword123"

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password=self.password,
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.other_customer = CustomUser.objects.create_user(
            email="customer2@test.com",
            password=self.password,
            user_name="Customer Two",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.payment = self.create_payment(customer=self.customer)

        self.url = reverse(
            "payments-api:payment-detail",
            kwargs={"payment_id": self.payment.id},
        )

    def authenticate(self, user):
        """Authenticate API client with the given user."""
        self.client.force_authenticate(user=user)

    def create_order(
        self,
        *,
        customer,
        amount=Decimal("100.00"),
    ):
        """Create and return an order with totals."""

        order = Order.objects.create(
            customer=customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

        OrderTotals.objects.create(
            order=order,
            subtotal=amount,
            grand_total=amount,
        )

        return order

    def create_payment(
        self,
        *,
        customer,
        amount=Decimal("100.00"),
        method=Payment.PAYMENT_METHOD_CREDIT_CARD,
        status_value=Payment.PAYMENT_STATUS_PENDING,
    ):
        """Create and return a payment."""

        order = self.create_order(
            customer=customer,
            amount=amount,
        )

        return Payment.objects.create(
            order=order,
            customer=customer,
            payment_reference=f"PAY-{uuid.uuid4().hex[:12].upper()}",
            method=method,
            status=status_value,
            amount=amount,
            refunded_amount=Decimal("0.00"),
            currency="USD",
            gateway_name="",
            gateway_payment_id="",
            gateway_customer_id="",
            metadata={},
        )

    def test_payment_detail_requires_authentication(self):
        """Reject payment detail request when unauthenticated."""

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_can_view_own_payment(self):
        """Return payment detail when requested by the owner."""

        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["id"],
            str(self.payment.id),
        )
        self.assertEqual(
            response.data["customer"],
            self.customer.id,
        )
        self.assertEqual(
            response.data["amount"],
            "100.00",
        )
        self.assertEqual(
            response.data["method"],
            Payment.PAYMENT_METHOD_CREDIT_CARD,
        )
        self.assertEqual(
            response.data["status"],
            Payment.PAYMENT_STATUS_PENDING,
        )

    def test_customer_cannot_view_other_customer_payment(self):
        """Reject access when customer tries to view another customer's payment."""

        self.authenticate(self.other_customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_payment_detail_returns_not_found_for_invalid_id(self):
        """Return 404 when payment does not exist."""

        self.authenticate(self.customer)

        url = reverse(
            "payments-api:payment-detail",
            kwargs={"payment_id": uuid.uuid4()},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)