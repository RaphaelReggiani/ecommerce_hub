from decimal import Decimal
from uuid import uuid4

from django.core.cache import cache
from django.test import TestCase

from ech.users.models import CustomUser
from ech.products.models import Product
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
from ech.orders.services.cache_service import invalidate_order_related_caches


class OrderCacheSelectorsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        cls.staff = CustomUser.objects.create_user(
            email="staff@company.com",
            password="StrongPassword123",
            user_name="Operations Staff",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        cls.product = Product.objects.create(
            name="Keyboard Pro",
            product_type=Product.KEYBOARD,
            brand="Logitech",
            sold_by=cls.staff,
            description="Keyboard",
            technical_information="Info",
            price=Decimal("150.00"),
            discount_price=Decimal("120.00"),
            is_active=True,
        )

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def create_order_with_related_data(self, *, status=Order.ORDER_STATUS_PENDING):
        order = Order.objects.create(
            customer=self.customer,
            status=status,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
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

        OrderLifecycle.objects.create(order=order)

        return order

    def test_get_order_by_id_returns_order_and_caches_result(self):
        """Return order by id and reuse cached result on subsequent calls."""
        order = self.create_order_with_related_data()

        first_result = get_order_by_id(order.id)
        second_result = get_order_by_id(order.id)

        self.assertIsNotNone(first_result)
        self.assertEqual(first_result.id, order.id)
        self.assertIsNotNone(second_result)
        self.assertEqual(second_result.id, order.id)

    def test_get_order_by_id_returns_none_and_caches_empty_result(self):
        """Return None for missing order and cache the empty result."""
        missing_order_id = uuid4()

        first_result = get_order_by_id(missing_order_id)
        second_result = get_order_by_id(missing_order_id)

        self.assertIsNone(first_result)
        self.assertIsNone(second_result)

    def test_get_order_by_id_returns_stale_data_until_cache_is_invalidated(self):
        """Return stale cached data until the cache is explicitly invalidated."""
        order = self.create_order_with_related_data(status=Order.ORDER_STATUS_PENDING)

        cached_order = get_order_by_id(order.id)
        self.assertEqual(cached_order.status, Order.ORDER_STATUS_PENDING)

        Order.objects.filter(id=order.id).update(status=Order.ORDER_STATUS_CONFIRMED)

        stale_order = get_order_by_id(order.id)
        self.assertEqual(stale_order.status, Order.ORDER_STATUS_PENDING)

    def test_get_order_by_id_returns_fresh_data_after_cache_invalidation(self):
        """Return fresh data after related order caches are invalidated."""
        order = self.create_order_with_related_data(status=Order.ORDER_STATUS_PENDING)

        cached_order = get_order_by_id(order.id)
        self.assertEqual(cached_order.status, Order.ORDER_STATUS_PENDING)

        Order.objects.filter(id=order.id).update(status=Order.ORDER_STATUS_CONFIRMED)
        order.refresh_from_db()

        invalidate_order_related_caches(order)

        fresh_order = get_order_by_id(order.id)
        self.assertEqual(fresh_order.status, Order.ORDER_STATUS_CONFIRMED)

    def test_get_order_detail_for_management_returns_order_and_caches_result(self):
        """Return order detail for management and cache the result."""
        order = self.create_order_with_related_data()

        first_result = get_order_detail_for_management(order.id)
        second_result = get_order_detail_for_management(order.id)

        self.assertIsNotNone(first_result)
        self.assertEqual(first_result.id, order.id)
        self.assertIsNotNone(second_result)
        self.assertEqual(second_result.id, order.id)

    def test_get_order_detail_for_management_returns_none_for_nonexistent_order(self):
        """Return None when management selector is called with nonexistent id."""
        missing_order_id = uuid4()

        first_result = get_order_detail_for_management(missing_order_id)
        second_result = get_order_detail_for_management(missing_order_id)

        self.assertIsNone(first_result)
        self.assertIsNone(second_result)

    def test_get_order_detail_for_management_returns_stale_data_until_cache_is_invalidated(self):
        """Return stale management detail until cache invalidation occurs."""
        order = self.create_order_with_related_data(status=Order.ORDER_STATUS_PENDING)

        cached_order = get_order_detail_for_management(order.id)
        self.assertEqual(cached_order.status, Order.ORDER_STATUS_PENDING)

        Order.objects.filter(id=order.id).update(status=Order.ORDER_STATUS_CONFIRMED)

        stale_order = get_order_detail_for_management(order.id)
        self.assertEqual(stale_order.status, Order.ORDER_STATUS_PENDING)

    def test_get_order_detail_for_management_returns_fresh_data_after_invalidation(self):
        """Return fresh management detail after cache invalidation."""
        order = self.create_order_with_related_data(status=Order.ORDER_STATUS_PENDING)

        cached_order = get_order_detail_for_management(order.id)
        self.assertEqual(cached_order.status, Order.ORDER_STATUS_PENDING)

        Order.objects.filter(id=order.id).update(status=Order.ORDER_STATUS_CONFIRMED)
        order.refresh_from_db()

        invalidate_order_related_caches(order)

        fresh_order = get_order_detail_for_management(order.id)
        self.assertEqual(fresh_order.status, Order.ORDER_STATUS_CONFIRMED)