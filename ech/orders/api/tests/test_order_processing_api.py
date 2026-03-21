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


class OrderStartProcessingApiTestCase(APITestCase):
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
            status=Order.ORDER_STATUS_CONFIRMED,
            payment_status=Order.PAYMENT_STATUS_AUTHORIZED,
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
            processing_at=None,
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
        return reverse(
            "orders-api:order-start-processing",
            kwargs={"order_id": order_id},
        )

    def test_start_processing_requires_authentication(self):
        """Require authentication to start order processing."""
        order = self.create_order_with_full_data(customer=self.customer)

        response = self.client.post(self.get_url(order.id))

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_start_processing_denied_for_non_management_user(self):
        """Deny starting order processing for non-management users."""
        self.authenticate(self.customer)

        order = self.create_order_with_full_data(customer=self.customer)

        response = self.client.post(self.get_url(order.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_start_processing_returns_404_when_order_does_not_exist(self):
        """Return 404 when attempting to start processing for nonexistent order."""
        self.authenticate(self.staff)

        response = self.client.post(self.get_url(uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    @patch("ech.orders.api.views.OrderStatusService.start_processing")
    def test_start_processing_successfully(self, mock_start_processing):
        """Start order processing successfully and return updated detail."""
        self.authenticate(self.staff)

        order = self.create_order_with_full_data(customer=self.customer)

        def side_effect():
            order.status = Order.ORDER_STATUS_PROCESSING
            order.shipping_status = Order.SHIPPING_STATUS_PREPARING
            order.save(update_fields=["status", "shipping_status"])

            order.lifecycle.processing_at = timezone.now()
            order.lifecycle.save(update_fields=["processing_at", "updated_at"])

            invalidate_order_related_caches(order)

        mock_start_processing.side_effect = side_effect

        response = self.client.post(self.get_url(order.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        order.lifecycle.refresh_from_db()

        self.assertEqual(order.status, Order.ORDER_STATUS_PROCESSING)
        self.assertEqual(response.data["id"], str(order.id))
        self.assertEqual(response.data["status"], Order.ORDER_STATUS_PROCESSING)
        self.assertEqual(response.data["shipping_status"], Order.SHIPPING_STATUS_PREPARING)
        self.assertIn("lifecycle", response.data)
        self.assertIsNotNone(response.data["lifecycle"]["processing_at"])

        mock_start_processing.assert_called_once()

    @patch("ech.orders.api.views.OrderStatusService.start_processing")
    def test_start_processing_returns_400_when_service_raises_order_error(self, mock_start_processing):
        """Return 400 when service raises a domain OrderError."""
        self.authenticate(self.staff)

        order = self.create_order_with_full_data(customer=self.customer)

        mock_start_processing.side_effect = OrderError("Business error")

        response = self.client.post(self.get_url(order.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Business error")

        mock_start_processing.assert_called_once()

    @patch("ech.orders.api.views.OrderStatusService.start_processing")
    def test_start_processing_returns_management_detail_payload(self, mock_start_processing):
        """Return full management payload after starting processing."""
        self.authenticate(self.staff)

        order = self.create_order_with_full_data(customer=self.customer)

        def side_effect():
            order.status = Order.ORDER_STATUS_PROCESSING
            order.save(update_fields=["status"])

            order.lifecycle.processing_at = timezone.now()
            order.lifecycle.save(update_fields=["processing_at", "updated_at"])

            invalidate_order_related_caches(order)

        mock_start_processing.side_effect = side_effect

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