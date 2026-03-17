from unittest.mock import patch
from decimal import Decimal
from uuid import uuid4
from django.core.cache import cache

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ech.orders.exceptions import OrderError
from ech.users.models import CustomUser
from ech.products.models import Product
from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
    OrderAddress,
    OrderLifecycle,
)


class OrderCancelApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.other_customer = CustomUser.objects.create_user(
            email="other@test.com",
            password="StrongPassword123",
            user_name="Other User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.product = Product.objects.create(
            name="Mouse Pro",
            product_type=Product.MOUSE,
            brand="Logitech",
            sold_by=self.customer,
            description="Mouse",
            technical_information="Info",
            price=Decimal("100.00"),
            discount_price=None,
            is_active=True,
        )

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.customer)

    def create_order(self, *, customer):
        order = Order.objects.create(
            customer=customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name_snapshot=self.product.name,
            product_type_snapshot=self.product.product_type,
            brand_snapshot=self.product.brand,
            quantity=1,
            unit_price=Decimal("100.00"),
            discount_price=None,
            total_price=Decimal("100.00"),
        )

        OrderTotals.objects.create(
            order=order,
            subtotal=Decimal("100.00"),
            discount_total=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            shipping_total=Decimal("0.00"),
            grand_total=Decimal("100.00"),
        )

        OrderAddress.objects.create(
            order=order,
            full_name="Test User",
            address_line="Street",
            city="City",
            state="State",
            country="Country",
            postal_code="00000",
            phone="",
        )

        OrderLifecycle.objects.create(order=order)

        return order

    def test_cancel_order_successfully(self):
        self.authenticate(self.customer)

        order = self.create_order(customer=self.customer)

        url = reverse("orders-api:order-cancel", kwargs={"order_id": order.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.ORDER_STATUS_CANCELLED)

        self.assertEqual(response.data["id"], str(order.id))
        self.assertEqual(response.data["status"], Order.ORDER_STATUS_CANCELLED)

    def test_cancel_order_requires_authentication(self):
        order = self.create_order(customer=self.customer)

        url = reverse("orders-api:order-cancel", kwargs={"order_id": order.id})

        response = self.client.post(url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_cancel_order_denied_for_non_owner(self):
        self.authenticate(self.other_customer)

        order = self.create_order(customer=self.customer)

        url = reverse("orders-api:order-cancel", kwargs={"order_id": order.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_order_returns_404_when_not_found(self):
        self.authenticate(self.customer)

        url = reverse("orders-api:order-cancel", kwargs={"order_id": uuid4()})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("ech.orders.api.views.CancelOrderService.execute")
    def test_cancel_order_returns_400_when_service_raises_order_error(self, mock_execute):
        self.authenticate(self.customer)

        order = self.create_order(customer=self.customer)

        mock_execute.side_effect = OrderError("Business error")

        url = reverse("orders-api:order-cancel", kwargs={"order_id": order.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Business error")

    def test_cancel_order_returns_updated_order_data(self):
        self.authenticate(self.customer)

        order = self.create_order(customer=self.customer)

        url = reverse("orders-api:order-cancel", kwargs={"order_id": order.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("items", response.data)
        self.assertIn("totals", response.data)
        self.assertIn("address", response.data)
        self.assertIn("events", response.data)
        self.assertIn("notes", response.data)