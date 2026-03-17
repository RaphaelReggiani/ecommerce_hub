from unittest.mock import patch
from decimal import Decimal
from uuid import uuid4

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.cache import cache

from ech.users.models import CustomUser
from ech.products.models import Product
from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
    OrderAddress,
    OrderLifecycle,
    OrderEvent,
    OrderNote,
)
from ech.orders.exceptions import OrderError

from ech.orders.services.cache_service import invalidate_order_related_caches


class OrderShipApiTestCase(APITestCase):
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

        self.staff = CustomUser.objects.create_user(
            email="staff@company.com",
            password="StrongPassword123",
            user_name="Operations Staff",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        self.product = Product.objects.create(
            name="Keyboard Pro",
            product_type=Product.KEYBOARD,
            brand="Logitech",
            sold_by=self.customer,
            description="Keyboard",
            technical_information="Info",
            price=Decimal("150.00"),
            discount_price=Decimal("120.00"),
            is_active=True,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_order_with_full_data(self, *, customer):
        order = Order.objects.create(
            customer=customer,
            status=Order.ORDER_STATUS_PROCESSING,
            payment_status=Order.PAYMENT_STATUS_CAPTURED,
            shipping_status=Order.SHIPPING_STATUS_PREPARING,
            currency="USD",
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name_snapshot=self.product.name,
            product_type_snapshot=self.product.product_type,
            brand_snapshot=self.product.brand,
            quantity=2,
            unit_price=Decimal("150.00"),
            discount_price=Decimal("120.00"),
            total_price=Decimal("240.00"),
        )

        OrderTotals.objects.create(
            order=order,
            subtotal=Decimal("300.00"),
            discount_total=Decimal("60.00"),
            tax_total=Decimal("0.00"),
            shipping_total=Decimal("0.00"),
            grand_total=Decimal("240.00"),
        )

        OrderAddress.objects.create(
            order=order,
            full_name="Test User",
            address_line="Street",
            city="City",
            state="State",
            country="Country",
            postal_code="00000",
            phone="123",
        )

        OrderLifecycle.objects.create(
            order=order,
            confirmed_at=timezone.now(),
            processing_at=timezone.now(),
            shipped_at=None,
            delivered_at=None,
            cancelled_at=None,
            refunded_at=None,
        )

        OrderEvent.objects.create(
            order=order,
            event_type=OrderEvent.TYPE_CREATED,
            performed_by=customer,
            metadata={"source": "test"},
        )

        OrderNote.objects.create(
            order=order,
            author=customer,
            message="Test note",
            is_internal=False,
        )

        return order

    def get_url(self, order_id):
        return reverse("orders-api:order-ship", kwargs={"order_id": order_id})

    def test_ship_order_requires_authentication(self):
        order = self.create_order_with_full_data(customer=self.customer)

        response = self.client.post(self.get_url(order.id))

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_ship_order_denied_for_non_management_user(self):
        self.authenticate(self.customer)

        order = self.create_order_with_full_data(customer=self.customer)

        response = self.client.post(self.get_url(order.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ship_order_returns_404_when_order_does_not_exist(self):
        self.authenticate(self.staff)

        response = self.client.post(self.get_url(uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    @patch("ech.orders.api.views.OrderStatusService.ship_order")
    def test_ship_order_successfully(self, mock_ship_order):
        self.authenticate(self.staff)

        order = self.create_order_with_full_data(customer=self.customer)

        def side_effect():
            order.status = Order.ORDER_STATUS_SHIPPED
            order.shipping_status = Order.SHIPPING_STATUS_SHIPPED
            order.save(update_fields=["status", "shipping_status"])

            order.lifecycle.shipped_at = timezone.now()
            order.lifecycle.save(update_fields=["shipped_at", "updated_at"])

            invalidate_order_related_caches(order)

        mock_ship_order.side_effect = side_effect

        response = self.client.post(self.get_url(order.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        order.lifecycle.refresh_from_db()

        self.assertEqual(order.status, Order.ORDER_STATUS_SHIPPED)
        self.assertEqual(order.shipping_status, Order.SHIPPING_STATUS_SHIPPED)
        self.assertEqual(response.data["id"], str(order.id))
        self.assertEqual(response.data["status"], Order.ORDER_STATUS_SHIPPED)
        self.assertEqual(response.data["shipping_status"], Order.SHIPPING_STATUS_SHIPPED)
        self.assertIn("lifecycle", response.data)
        self.assertIsNotNone(response.data["lifecycle"]["shipped_at"])

        mock_ship_order.assert_called_once()

    @patch("ech.orders.api.views.OrderStatusService.ship_order")
    def test_ship_order_returns_400_when_service_raises_order_error(self, mock_ship_order):
        self.authenticate(self.staff)

        order = self.create_order_with_full_data(customer=self.customer)

        mock_ship_order.side_effect = OrderError("Business error")

        response = self.client.post(self.get_url(order.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Business error")

        mock_ship_order.assert_called_once()

    @patch("ech.orders.api.views.OrderStatusService.ship_order")
    def test_ship_order_returns_management_detail_payload(self, mock_ship_order):
        self.authenticate(self.staff)

        order = self.create_order_with_full_data(customer=self.customer)

        def side_effect():
            order.status = Order.ORDER_STATUS_SHIPPED
            order.shipping_status = Order.SHIPPING_STATUS_SHIPPED
            order.save(update_fields=["status", "shipping_status"])

            order.lifecycle.shipped_at = timezone.now()
            order.lifecycle.save(update_fields=["shipped_at", "updated_at"])

            invalidate_order_related_caches(order)

        mock_ship_order.side_effect = side_effect

        response = self.client.post(self.get_url(order.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("items", response.data)
        self.assertIn("totals", response.data)
        self.assertIn("address", response.data)
        self.assertIn("lifecycle", response.data)
        self.assertIn("events", response.data)
        self.assertIn("notes", response.data)

        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["totals"]["grand_total"], "240.00")
        self.assertEqual(response.data["address"]["full_name"], "Test User")