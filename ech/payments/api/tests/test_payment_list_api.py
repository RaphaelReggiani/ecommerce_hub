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


class PaymentListApiTestCase(APITestCase):

    def setUp(self):
        """Set up common test data for payment list API tests."""

        cache.clear()

        self.url = reverse("payments-api:payment-list")
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

        self.staff = CustomUser.objects.create_user(
            email="staff@company.com",
            password=self.password,
            user_name="Payment Staff",
            role=CustomUser.ROLE_PAYMENT_STAFF,
            is_active=True,
            email_confirmed=True,
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
        refunded_amount=Decimal("0.00"),
    ):
        """Create and return a payment for the given customer."""

        order = self.create_order(customer=customer, amount=amount)

        return Payment.objects.create(
            order=order,
            customer=customer,
            payment_reference=f"PAY-{uuid.uuid4().hex[:12].upper()}",
            method=method,
            status=status_value,
            amount=amount,
            refunded_amount=refunded_amount,
            currency="USD",
            gateway_name="",
            gateway_payment_id="",
            gateway_customer_id="",
            metadata={},
        )

    def test_list_payments_requires_authentication(self):
        """Reject payment list request when unauthenticated."""

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_sees_only_own_payments(self):
        """Return only payments belonging to the authenticated customer."""

        own_payment = self.create_payment(customer=self.customer)
        self.create_payment(customer=self.other_customer)

        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(own_payment.id),
        )
        self.assertEqual(
            response.data["results"][0]["customer"],
            self.customer.id,
        )

    def test_staff_sees_all_payments(self):
        """Return all payments when user has payment staff role."""

        self.create_payment(customer=self.customer)
        self.create_payment(customer=self.other_customer)

        self.authenticate(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_list_payments_returns_paginated_results(self):
        """Return paginated payment results."""

        for _ in range(15):
            self.create_payment(customer=self.customer)

        self.authenticate(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertLessEqual(len(response.data["results"]), 20)

    def test_filter_payments_by_method(self):
        """Return only payments matching the provided payment method."""

        pix_payment = self.create_payment(
            customer=self.customer,
            method=Payment.PAYMENT_METHOD_PIX,
        )
        self.create_payment(
            customer=self.customer,
            method=Payment.PAYMENT_METHOD_CREDIT_CARD,
        )

        self.authenticate(self.customer)

        response = self.client.get(
            self.url,
            {"method": Payment.PAYMENT_METHOD_PIX},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(pix_payment.id),
        )
        self.assertEqual(
            response.data["results"][0]["method"],
            Payment.PAYMENT_METHOD_PIX,
        )

    def test_filter_payments_by_status(self):
        """Return only payments matching the provided payment status."""

        captured_payment = self.create_payment(
            customer=self.customer,
            status_value=Payment.PAYMENT_STATUS_CAPTURED,
        )
        self.create_payment(
            customer=self.customer,
            status_value=Payment.PAYMENT_STATUS_PENDING,
        )

        self.authenticate(self.customer)

        response = self.client.get(
            self.url,
            {"status": Payment.PAYMENT_STATUS_CAPTURED},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(captured_payment.id),
        )
        self.assertEqual(
            response.data["results"][0]["status"],
            Payment.PAYMENT_STATUS_CAPTURED,
        )

    def test_filter_payments_by_is_refunded(self):
        """Return only fully refunded payments when is_refunded is true."""

        refunded_payment = self.create_payment(
            customer=self.customer,
            amount=Decimal("100.00"),
            refunded_amount=Decimal("100.00"),
            status_value=Payment.PAYMENT_STATUS_REFUNDED,
        )
        self.create_payment(
            customer=self.customer,
            amount=Decimal("100.00"),
            refunded_amount=Decimal("20.00"),
            status_value=Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
        )

        self.authenticate(self.customer)

        response = self.client.get(
            self.url,
            {"is_refunded": True},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(refunded_payment.id),
        )

    def test_filter_payments_by_is_partially_refunded(self):
        """Return only partially refunded payments when is_partially_refunded is true."""

        partial_payment = self.create_payment(
            customer=self.customer,
            amount=Decimal("100.00"),
            refunded_amount=Decimal("20.00"),
            status_value=Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
        )
        self.create_payment(
            customer=self.customer,
            amount=Decimal("100.00"),
            refunded_amount=Decimal("100.00"),
            status_value=Payment.PAYMENT_STATUS_REFUNDED,
        )

        self.authenticate(self.customer)

        response = self.client.get(
            self.url,
            {"is_partially_refunded": True},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(partial_payment.id),
        )