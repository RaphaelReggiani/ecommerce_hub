from decimal import Decimal

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


class PaymentCreateApiTestCase(APITestCase):

    def setUp(self):
        """Set up common test data for payment creation API tests."""

        cache.clear()

        self.url = reverse("payments-api:payment-create")
        self.password = "StrongPassword123"

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password=self.password,
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.order = self.create_order(customer=self.customer)

    def authenticate(self, user):
        """Authenticate API client with the given user."""
        self.client.force_authenticate(user=user)

    def create_order(
        self,
        *,
        customer,
        status_value=Order.ORDER_STATUS_PENDING,
        payment_status=Order.PAYMENT_STATUS_PENDING,
        shipping_status=Order.SHIPPING_STATUS_PENDING,
        currency="USD",
        subtotal=Decimal("115.00"),
        grand_total=Decimal("115.00"),
    ):
        """Create and return an order with totals."""

        order = Order.objects.create(
            customer=customer,
            status=status_value,
            payment_status=payment_status,
            shipping_status=shipping_status,
            currency=currency,
        )

        OrderTotals.objects.create(
            order=order,
            subtotal=subtotal,
            grand_total=grand_total,
        )

        return order

    def get_payload(self, *, order=None):
        """Return a valid payload for payment creation."""

        target_order = order or self.order

        return {
            "order_id": str(target_order.id),
            "method": Payment.PAYMENT_METHOD_CREDIT_CARD,
        }

    def test_create_payment_requires_authentication(self):
        """Reject payment creation when the request is unauthenticated."""

        response = self.client.post(self.url, self.get_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_payment_success(self):
        """Create payment successfully for a valid order."""

        self.authenticate(self.customer)

        response = self.client.post(self.url, self.get_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        payment = Payment.objects.get(order=self.order)

        self.assertEqual(payment.order_id, self.order.id)
        self.assertEqual(payment.customer_id, self.customer.id)
        self.assertEqual(payment.amount, Decimal("115.00"))
        self.assertEqual(payment.refunded_amount, Decimal("0.00"))
        self.assertEqual(payment.currency, "USD")
        self.assertEqual(payment.method, Payment.PAYMENT_METHOD_CREDIT_CARD)
        self.assertEqual(payment.status, Payment.PAYMENT_STATUS_PENDING)

    def test_create_payment_with_gateway_fields(self):
        """Create payment successfully with gateway-related fields."""

        self.authenticate(self.customer)

        payload = self.get_payload()
        payload.update(
            {
                "gateway_name": "stripe",
                "gateway_payment_id": "pay_123",
                "gateway_customer_id": "cust_456",
            }
        )

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        payment = Payment.objects.get(order=self.order)

        self.assertEqual(payment.gateway_name, "stripe")
        self.assertEqual(payment.gateway_payment_id, "pay_123")
        self.assertEqual(payment.gateway_customer_id, "cust_456")

    def test_create_payment_with_metadata(self):
        """Create payment successfully with metadata."""

        self.authenticate(self.customer)

        payload = self.get_payload()
        payload["metadata"] = {"source": "mobile"}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        payment = Payment.objects.get(order=self.order)

        self.assertEqual(payment.metadata, {"source": "mobile"})

    def test_create_payment_with_idempotency_key(self):
        """Create payment successfully when idempotency key is provided."""

        self.authenticate(self.customer)

        payload = self.get_payload()
        payload["idempotency_key"] = "11111111-1111-1111-1111-111111111111"

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        payment = Payment.objects.get(order=self.order)

        self.assertEqual(
            str(payment.idempotency_key),
            "11111111-1111-1111-1111-111111111111",
        )

    def test_create_payment_order_not_found(self):
        """Reject payment creation when the order does not exist."""

        self.authenticate(self.customer)

        payload = {
            "order_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "method": Payment.PAYMENT_METHOD_CREDIT_CARD,
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.count(), 0)

    def test_create_payment_duplicate_for_same_order(self):
        """Reject payment creation when a payment already exists for the order."""

        self.authenticate(self.customer)

        first_response = self.client.post(self.url, self.get_payload(), format="json")
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.url, self.get_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.count(), 1)

    def test_duplicate_idempotency_key_is_blocked(self):
        """Reject payment creation when idempotency key is reused."""

        self.authenticate(self.customer)

        second_order = self.create_order(
            customer=self.customer,
            subtotal=Decimal("60.00"),
            grand_total=Decimal("60.00"),
        )

        idempotency_key = "22222222-2222-2222-2222-222222222222"

        first_payload = self.get_payload(order=self.order)
        first_payload["idempotency_key"] = idempotency_key

        second_payload = self.get_payload(order=second_order)
        second_payload["idempotency_key"] = idempotency_key

        first_response = self.client.post(self.url, first_payload, format="json")
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.url, second_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.count(), 1)

    def test_duplicate_payment_reference_is_blocked(self):
        """Reject payment creation when payment reference already exists."""

        self.authenticate(self.customer)

        second_order = self.create_order(
            customer=self.customer,
            subtotal=Decimal("80.00"),
            grand_total=Decimal("80.00"),
        )

        payment_reference = "PAY-TEST-123"

        first_payload = self.get_payload(order=self.order)
        first_payload["payment_reference"] = payment_reference

        second_payload = self.get_payload(order=second_order)
        second_payload["payment_reference"] = payment_reference

        first_response = self.client.post(self.url, first_payload, format="json")
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.url, second_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.count(), 1)