from decimal import Decimal
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from ech.users.models import CustomUser
from ech.products.models import Product, ProductInventory
from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
    OrderAddress,
    OrderLifecycle,
)
from ech.orders.selectors import (
    get_order_by_id,
    get_order_detail_for_management,
)
from ech.orders.services.order_create_service import CreateOrderService
from ech.orders.services.order_cancel_service import CancelOrderService
from ech.orders.services.order_status_service import OrderStatusService


class OrderCacheInvalidationTestCase(TestCase):
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

        self.inventory = ProductInventory.objects.create(
            product=self.product,
            quantity=20,
        )

        self.valid_items = [
            {
                "product_id": self.product.id,
                "quantity": 2,
            }
        ]

        self.valid_address = {
            "full_name": "User Tester",
            "address_line": "Rua Teste, 123",
            "city": "Sao Paulo",
            "state": "SP",
            "country": "Brazil",
            "postal_code": "01234-567",
            "phone": "11999999999",
        }

    def tearDown(self):
        cache.clear()

    def create_order_with_related_data(
        self,
        *,
        customer=None,
        status=Order.ORDER_STATUS_PENDING,
        payment_status=Order.PAYMENT_STATUS_PENDING,
        shipping_status=Order.SHIPPING_STATUS_PENDING,
        lifecycle_confirmed_at=None,
        lifecycle_processing_at=None,
        lifecycle_shipped_at=None,
        lifecycle_delivered_at=None,
        lifecycle_cancelled_at=None,
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
            confirmed_at=lifecycle_confirmed_at,
            processing_at=lifecycle_processing_at,
            shipped_at=lifecycle_shipped_at,
            delivered_at=lifecycle_delivered_at,
            cancelled_at=lifecycle_cancelled_at,
            refunded_at=None,
        )

        return order

    @patch("ech.orders.services.order_create_service.invalidate_order_related_caches")
    def test_create_order_service_invalidates_order_related_caches(self, mock_invalidate):
        service = CreateOrderService(
            customer=self.customer,
            items=self.valid_items,
            address=self.valid_address,
        )

        order = service.execute()

        mock_invalidate.assert_called_once_with(order)

    @patch("ech.orders.services.order_cancel_service.invalidate_order_related_caches")
    def test_cancel_order_service_invalidates_order_related_caches(self, mock_invalidate):
        order = self.create_order_with_related_data(
            status=Order.ORDER_STATUS_PENDING,
        )

        service = CancelOrderService(
            order=order,
            performed_by=self.customer,
        )

        result = service.execute()

        order.refresh_from_db()

        self.assertEqual(order.status, Order.ORDER_STATUS_CANCELLED)
        self.assertEqual(result.id, order.id)
        mock_invalidate.assert_called_once()
        self.assertEqual(mock_invalidate.call_args[0][0].id, order.id)

    def test_cancel_order_service_returns_fresh_detail_after_invalidation(self):
        order = self.create_order_with_related_data(
            status=Order.ORDER_STATUS_PENDING,
        )

        cached_order = get_order_by_id(order.id)
        self.assertEqual(cached_order.status, Order.ORDER_STATUS_PENDING)

        service = CancelOrderService(
            order=order,
            performed_by=self.customer,
        )
        service.execute()

        fresh_order = get_order_by_id(order.id)
        self.assertEqual(fresh_order.status, Order.ORDER_STATUS_CANCELLED)

    @patch("ech.orders.services.order_status_service.invalidate_order_related_caches")
    def test_confirm_order_invalidates_order_related_caches(self, mock_invalidate):
        order = self.create_order_with_related_data(
            status=Order.ORDER_STATUS_PENDING,
        )

        service = OrderStatusService(
            order=order,
            performed_by=self.staff,
        )

        result = service.confirm_order()

        order.refresh_from_db()

        self.assertEqual(order.status, Order.ORDER_STATUS_CONFIRMED)
        self.assertEqual(result.id, order.id)
        mock_invalidate.assert_called_once()
        self.assertEqual(mock_invalidate.call_args[0][0].id, order.id)

    def test_confirm_order_returns_fresh_detail_after_cache_invalidation(self):
        order = self.create_order_with_related_data(
            status=Order.ORDER_STATUS_PENDING,
        )

        cached_order = get_order_detail_for_management(order.id)
        self.assertEqual(cached_order.status, Order.ORDER_STATUS_PENDING)

        service = OrderStatusService(
            order=order,
            performed_by=self.staff,
        )
        service.confirm_order()

        fresh_order = get_order_detail_for_management(order.id)
        self.assertEqual(fresh_order.status, Order.ORDER_STATUS_CONFIRMED)

    @patch("ech.orders.services.order_status_service.invalidate_order_related_caches")
    def test_start_processing_invalidates_order_related_caches(self, mock_invalidate):
        order = self.create_order_with_related_data(
            status=Order.ORDER_STATUS_CONFIRMED,
            lifecycle_confirmed_at=timezone.now(),
        )

        service = OrderStatusService(
            order=order,
            performed_by=self.staff,
        )

        result = service.start_processing()

        order.refresh_from_db()

        self.assertEqual(order.status, Order.ORDER_STATUS_PROCESSING)
        self.assertEqual(result.id, order.id)
        mock_invalidate.assert_called_once()
        self.assertEqual(mock_invalidate.call_args[0][0].id, order.id)

    def test_start_processing_returns_fresh_detail_after_cache_invalidation(self):
        order = self.create_order_with_related_data(
            status=Order.ORDER_STATUS_CONFIRMED,
            lifecycle_confirmed_at=timezone.now(),
        )

        cached_order = get_order_detail_for_management(order.id)
        self.assertEqual(cached_order.status, Order.ORDER_STATUS_CONFIRMED)

        service = OrderStatusService(
            order=order,
            performed_by=self.staff,
        )
        service.start_processing()

        fresh_order = get_order_detail_for_management(order.id)
        self.assertEqual(fresh_order.status, Order.ORDER_STATUS_PROCESSING)

    @patch("ech.orders.services.order_status_service.invalidate_order_related_caches")
    def test_ship_order_invalidates_order_related_caches(self, mock_invalidate):
        order = self.create_order_with_related_data(
            status=Order.ORDER_STATUS_PROCESSING,
            shipping_status=Order.SHIPPING_STATUS_PREPARING,
            lifecycle_confirmed_at=timezone.now(),
            lifecycle_processing_at=timezone.now(),
        )

        service = OrderStatusService(
            order=order,
            performed_by=self.staff,
        )

        result = service.ship_order()

        order.refresh_from_db()

        self.assertEqual(order.status, Order.ORDER_STATUS_SHIPPED)
        self.assertEqual(order.shipping_status, Order.SHIPPING_STATUS_SHIPPED)
        self.assertEqual(result.id, order.id)
        mock_invalidate.assert_called_once()
        self.assertEqual(mock_invalidate.call_args[0][0].id, order.id)

    def test_ship_order_returns_fresh_detail_after_cache_invalidation(self):
        order = self.create_order_with_related_data(
            status=Order.ORDER_STATUS_PROCESSING,
            shipping_status=Order.SHIPPING_STATUS_PREPARING,
            lifecycle_confirmed_at=timezone.now(),
            lifecycle_processing_at=timezone.now(),
        )

        cached_order = get_order_detail_for_management(order.id)
        self.assertEqual(cached_order.status, Order.ORDER_STATUS_PROCESSING)

        service = OrderStatusService(
            order=order,
            performed_by=self.staff,
        )
        service.ship_order()

        fresh_order = get_order_detail_for_management(order.id)
        self.assertEqual(fresh_order.status, Order.ORDER_STATUS_SHIPPED)
        self.assertEqual(fresh_order.shipping_status, Order.SHIPPING_STATUS_SHIPPED)

    @patch("ech.orders.services.order_status_service.invalidate_order_related_caches")
    def test_deliver_order_invalidates_order_related_caches(self, mock_invalidate):
        order = self.create_order_with_related_data(
            status=Order.ORDER_STATUS_SHIPPED,
            shipping_status=Order.SHIPPING_STATUS_SHIPPED,
            lifecycle_confirmed_at=timezone.now(),
            lifecycle_processing_at=timezone.now(),
            lifecycle_shipped_at=timezone.now(),
        )

        service = OrderStatusService(
            order=order,
            performed_by=self.staff,
        )

        result = service.deliver_order()

        order.refresh_from_db()

        self.assertEqual(order.status, Order.ORDER_STATUS_DELIVERED)
        self.assertEqual(order.shipping_status, Order.SHIPPING_STATUS_DELIVERED)
        self.assertEqual(result.id, order.id)
        mock_invalidate.assert_called_once()
        self.assertEqual(mock_invalidate.call_args[0][0].id, order.id)

    def test_deliver_order_returns_fresh_detail_after_cache_invalidation(self):
        order = self.create_order_with_related_data(
            status=Order.ORDER_STATUS_SHIPPED,
            shipping_status=Order.SHIPPING_STATUS_SHIPPED,
            lifecycle_confirmed_at=timezone.now(),
            lifecycle_processing_at=timezone.now(),
            lifecycle_shipped_at=timezone.now(),
        )

        cached_order = get_order_detail_for_management(order.id)
        self.assertEqual(cached_order.status, Order.ORDER_STATUS_SHIPPED)

        service = OrderStatusService(
            order=order,
            performed_by=self.staff,
        )
        service.deliver_order()

        fresh_order = get_order_detail_for_management(order.id)
        self.assertEqual(fresh_order.status, Order.ORDER_STATUS_DELIVERED)
        self.assertEqual(fresh_order.shipping_status, Order.SHIPPING_STATUS_DELIVERED)