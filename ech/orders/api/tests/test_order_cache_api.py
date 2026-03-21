from decimal import Decimal

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser
from ech.products.models import Product
from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
    OrderAddress,
    OrderLifecycle,
)
from ech.orders.services.order_cancel_service import CancelOrderService
from ech.orders.services.order_status_service import OrderStatusService


class OrderCacheApiTestCase(APITestCase):
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
            sold_by=self.staff,
            description="Keyboard",
            technical_information="Info",
            price=Decimal("150.00"),
            discount_price=Decimal("120.00"),
            is_active=True,
        )

    def tearDown(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_order_with_full_data(
        self,
        *,
        customer=None,
        status=Order.ORDER_STATUS_PENDING,
        payment_status=Order.PAYMENT_STATUS_PENDING,
        shipping_status=Order.SHIPPING_STATUS_PENDING,
        confirmed_at=None,
        processing_at=None,
        shipped_at=None,
        delivered_at=None,
        cancelled_at=None,
    ):
        customer = customer or self.customer

        order = Order.objects.create(
            customer=customer,
            status=status,
            payment_status=payment_status,
            shipping_status=shipping_status,
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
            address_line="Street 123",
            city="Sao Paulo",
            state="SP",
            country="Brazil",
            postal_code="00000-000",
            phone="11999999999",
        )

        OrderLifecycle.objects.create(
            order=order,
            confirmed_at=confirmed_at,
            processing_at=processing_at,
            shipped_at=shipped_at,
            delivered_at=delivered_at,
            cancelled_at=cancelled_at,
            refunded_at=None,
        )

        return order

    def test_order_detail_returns_fresh_data_after_order_cancellation(self):
        """Return fresh order detail after order cancellation invalidates cache."""
        order = self.create_order_with_full_data(
            status=Order.ORDER_STATUS_PENDING,
        )

        detail_url = reverse("orders-api:order-detail", kwargs={"order_id": order.id})

        self.authenticate(self.customer)

        first_response = self.client.get(detail_url)

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(first_response.data["status"], Order.ORDER_STATUS_PENDING)

        service = CancelOrderService(
            order=order,
            performed_by=self.customer,
        )
        service.execute()

        second_response = self.client.get(detail_url)

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.data["status"], Order.ORDER_STATUS_CANCELLED)

    def test_management_detail_returns_fresh_data_after_order_confirmation(self):
        """Return fresh management detail after order confirmation."""
        order = self.create_order_with_full_data(
            status=Order.ORDER_STATUS_PENDING,
        )

        detail_url = reverse(
            "orders-api:order-management-detail",
            kwargs={"order_id": order.id},
        )

        self.authenticate(self.staff)

        first_response = self.client.get(detail_url)

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(first_response.data["status"], Order.ORDER_STATUS_PENDING)

        service = OrderStatusService(
            order=order,
            performed_by=self.staff,
        )
        service.confirm_order()

        second_response = self.client.get(detail_url)

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.data["status"], Order.ORDER_STATUS_CONFIRMED)

    def test_management_detail_returns_fresh_data_after_start_processing(self):
        """Return fresh management detail after starting order processing."""
        order = self.create_order_with_full_data(
            status=Order.ORDER_STATUS_CONFIRMED,
            confirmed_at=order_time(),
        )

        detail_url = reverse(
            "orders-api:order-management-detail",
            kwargs={"order_id": order.id},
        )

        self.authenticate(self.staff)

        first_response = self.client.get(detail_url)

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(first_response.data["status"], Order.ORDER_STATUS_CONFIRMED)

        service = OrderStatusService(
            order=order,
            performed_by=self.staff,
        )
        service.start_processing()

        second_response = self.client.get(detail_url)

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.data["status"], Order.ORDER_STATUS_PROCESSING)

    def test_management_detail_returns_fresh_data_after_shipping(self):
        """Return fresh management detail after shipping an order."""
        now = order_time()

        order = self.create_order_with_full_data(
            status=Order.ORDER_STATUS_PROCESSING,
            shipping_status=Order.SHIPPING_STATUS_PREPARING,
            confirmed_at=now,
            processing_at=now,
        )

        detail_url = reverse(
            "orders-api:order-management-detail",
            kwargs={"order_id": order.id},
        )

        self.authenticate(self.staff)

        first_response = self.client.get(detail_url)

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(first_response.data["status"], Order.ORDER_STATUS_PROCESSING)
        self.assertEqual(
            first_response.data["shipping_status"],
            Order.SHIPPING_STATUS_PREPARING,
        )

        service = OrderStatusService(
            order=order,
            performed_by=self.staff,
        )
        service.ship_order()

        second_response = self.client.get(detail_url)

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.data["status"], Order.ORDER_STATUS_SHIPPED)
        self.assertEqual(
            second_response.data["shipping_status"],
            Order.SHIPPING_STATUS_SHIPPED,
        )

    def test_management_detail_returns_fresh_data_after_delivery(self):
        """Return fresh management detail after delivering an order."""
        now = order_time()

        order = self.create_order_with_full_data(
            status=Order.ORDER_STATUS_SHIPPED,
            shipping_status=Order.SHIPPING_STATUS_SHIPPED,
            confirmed_at=now,
            processing_at=now,
            shipped_at=now,
        )

        detail_url = reverse(
            "orders-api:order-management-detail",
            kwargs={"order_id": order.id},
        )

        self.authenticate(self.staff)

        first_response = self.client.get(detail_url)

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(first_response.data["status"], Order.ORDER_STATUS_SHIPPED)
        self.assertEqual(
            first_response.data["shipping_status"],
            Order.SHIPPING_STATUS_SHIPPED,
        )

        service = OrderStatusService(
            order=order,
            performed_by=self.staff,
        )
        service.deliver_order()

        second_response = self.client.get(detail_url)

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.data["status"], Order.ORDER_STATUS_DELIVERED)
        self.assertEqual(
            second_response.data["shipping_status"],
            Order.SHIPPING_STATUS_DELIVERED,
        )

    def test_repeated_order_detail_requests_return_consistent_data(self):
        """Return consistent order detail data across repeated requests."""
        order = self.create_order_with_full_data(
            status=Order.ORDER_STATUS_PENDING,
        )

        detail_url = reverse("orders-api:order-detail", kwargs={"order_id": order.id})

        self.authenticate(self.customer)

        first_response = self.client.get(detail_url)
        second_response = self.client.get(detail_url)

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)

        self.assertEqual(first_response.data["id"], second_response.data["id"])
        self.assertEqual(first_response.data["status"], second_response.data["status"])
        self.assertEqual(
            first_response.data["shipping_status"],
            second_response.data["shipping_status"],
        )
        self.assertEqual(
            first_response.data["payment_status"],
            second_response.data["payment_status"],
        )


def order_time():
    from django.utils import timezone

    return timezone.now()