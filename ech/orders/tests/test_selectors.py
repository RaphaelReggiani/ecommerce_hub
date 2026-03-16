from decimal import Decimal
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db import transaction

from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
    OrderAddress,
    OrderLifecycle,
    OrderEvent,
    OrderNote,
)
from ech.orders.selectors import (
    get_order_by_id,
    list_orders_by_customer,
    list_orders_by_status,
    list_orders_by_payment_status,
    list_orders_by_shipping_status,
    list_recent_orders,
    list_all_orders,
    get_order_for_update,
    list_orders_for_management,
    get_order_detail_for_management,
)
from ech.products.models import Product


class BaseSelectorFactoryMixin:
    user_counter = 0
    product_counter = 0

    def create_user(self, **overrides):
        User = get_user_model()
        self.__class__.user_counter += 1
        idx = self.__class__.user_counter

        model_fields = {field.name: field for field in User._meta.fields}
        unique_suffix = uuid.uuid4().hex[:8]
        unique_email = f"user_{idx}_{unique_suffix}@test.com"

        data = {}

        if "email" in model_fields:
            data["email"] = unique_email

        if "user_email" in model_fields:
            data["user_email"] = unique_email

        if "username" in model_fields:
            data["username"] = f"user_{idx}_{unique_suffix}"

        if "user_name" in model_fields:
            data["user_name"] = f"Test User {idx}"

        if "first_name" in model_fields:
            data["first_name"] = "Test"

        if "last_name" in model_fields:
            data["last_name"] = f"User{idx}"

        if "is_active" in model_fields:
            data["is_active"] = True

        data.update(overrides)

        manager = User.objects

        if hasattr(manager, "create_user"):
            try:
                return manager.create_user(password="StrongPass123!", **data)
            except TypeError:
                pass
            except Exception:
                pass

        user = manager.create(**data)

        if hasattr(user, "set_password"):
            user.set_password("StrongPass123!")
            user.save(update_fields=["password"])

        return user

    def create_product(self, **overrides):
        self.__class__.product_counter += 1
        idx = self.__class__.product_counter

        data = {
            "name": f"Product {idx}",
            "product_type": Product.MOUSE,
            "brand": "Test Brand",
            "sold_by": self.create_user(),
            "description": "Test product description.",
            "technical_information": "Test technical information.",
            "price": Decimal("100.00"),
            "discount_price": Decimal("90.00"),
            "is_active": True,
        }
        data.update(overrides)
        return Product.objects.create(**data)

    def create_order(self, **overrides):
        data = {
            "customer": self.create_user(),
            "status": Order.ORDER_STATUS_PENDING,
            "payment_status": Order.PAYMENT_STATUS_PENDING,
            "shipping_status": Order.SHIPPING_STATUS_PENDING,
            "currency": "USD",
        }
        data.update(overrides)
        return Order.objects.create(**data)

    def create_full_order(self, **overrides):
        order = self.create_order(**overrides)
        product = self.create_product()

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name_snapshot="Test Mouse",
            product_type_snapshot=Product.MOUSE,
            brand_snapshot="Test Brand",
            quantity=2,
            unit_price=Decimal("50.00"),
            discount_price=Decimal("5.00"),
            total_price=Decimal("95.00"),
        )

        OrderTotals.objects.create(
            order=order,
            subtotal=Decimal("100.00"),
            discount_total=Decimal("10.00"),
            tax_total=Decimal("5.00"),
            shipping_total=Decimal("15.00"),
            grand_total=Decimal("110.00"),
        )

        OrderAddress.objects.create(
            order=order,
            full_name="Test Customer",
            address_line="123 Test Street",
            city="Test City",
            state="TS",
            country="Test Country",
            postal_code="00000-000",
            phone="+00 00000-0000",
        )

        OrderLifecycle.objects.create(order=order)

        OrderEvent.objects.create(
            order=order,
            event_type=OrderEvent.TYPE_CREATED,
            performed_by=self.create_user(),
            metadata={"source": "test"},
        )

        OrderNote.objects.create(
            order=order,
            author=self.create_user(),
            message="Test note.",
            is_internal=False,
        )

        return order


class GetOrderByIdSelectorTestCase(BaseSelectorFactoryMixin, TestCase):
    def test_get_order_by_id_returns_order_when_found(self):
        order = self.create_full_order()

        result = get_order_by_id(order.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, order.id)

    def test_get_order_by_id_returns_none_when_not_found(self):
        result = get_order_by_id(uuid.uuid4())

        self.assertIsNone(result)

    def test_get_order_by_id_returns_related_data_accessibly(self):
        order = self.create_full_order()

        result = get_order_by_id(order.id)

        self.assertEqual(result.customer, order.customer)
        self.assertEqual(result.totals.order, order)
        self.assertEqual(result.address.order, order)
        self.assertEqual(result.lifecycle.order, order)
        self.assertEqual(result.items.count(), 1)
        self.assertEqual(result.events.count(), 1)
        self.assertEqual(result.notes.count(), 1)


class ListOrdersByCustomerSelectorTestCase(BaseSelectorFactoryMixin, TestCase):
    def test_list_orders_by_customer_returns_only_orders_from_given_customer(self):
        customer = self.create_user()
        other_customer = self.create_user()

        first_order = self.create_order(customer=customer)
        second_order = self.create_order(customer=customer)
        self.create_order(customer=other_customer)

        results = list(list_orders_by_customer(customer))

        self.assertEqual(len(results), 2)
        self.assertIn(first_order, results)
        self.assertIn(second_order, results)

    def test_list_orders_by_customer_returns_empty_queryset_when_customer_has_no_orders(self):
        customer = self.create_user()

        results = list_orders_by_customer(customer)

        self.assertEqual(results.count(), 0)

    def test_list_orders_by_customer_returns_orders_ordered_by_created_at_desc(self):
        customer = self.create_user()

        older = self.create_order(customer=customer)
        newer = self.create_order(customer=customer)

        results = list(list_orders_by_customer(customer))

        self.assertEqual(results[0], newer)
        self.assertEqual(results[1], older)


class ListOrdersByStatusSelectorTestCase(BaseSelectorFactoryMixin, TestCase):
    def test_list_orders_by_status_returns_only_matching_status(self):
        pending_order = self.create_order(status=Order.ORDER_STATUS_PENDING)
        second_pending_order = self.create_order(status=Order.ORDER_STATUS_PENDING)
        self.create_order(status=Order.ORDER_STATUS_CANCELLED)

        results = list(list_orders_by_status(Order.ORDER_STATUS_PENDING))

        self.assertEqual(len(results), 2)
        self.assertIn(pending_order, results)
        self.assertIn(second_pending_order, results)

    def test_list_orders_by_status_returns_empty_queryset_when_no_match(self):
        self.create_order(status=Order.ORDER_STATUS_CANCELLED)

        results = list_orders_by_status(Order.ORDER_STATUS_DELIVERED)

        self.assertEqual(results.count(), 0)

    def test_list_orders_by_status_returns_orders_ordered_by_created_at_desc(self):
        older = self.create_order(status=Order.ORDER_STATUS_PENDING)
        newer = self.create_order(status=Order.ORDER_STATUS_PENDING)

        results = list(list_orders_by_status(Order.ORDER_STATUS_PENDING))

        self.assertEqual(results[0], newer)
        self.assertEqual(results[1], older)


class ListOrdersByPaymentStatusSelectorTestCase(BaseSelectorFactoryMixin, TestCase):
    def test_list_orders_by_payment_status_returns_only_matching_payment_status(self):
        first_order = self.create_order(payment_status=Order.PAYMENT_STATUS_PENDING)
        second_order = self.create_order(payment_status=Order.PAYMENT_STATUS_PENDING)
        self.create_order(payment_status=Order.PAYMENT_STATUS_CAPTURED)

        results = list(list_orders_by_payment_status(Order.PAYMENT_STATUS_PENDING))

        self.assertEqual(len(results), 2)
        self.assertIn(first_order, results)
        self.assertIn(second_order, results)

    def test_list_orders_by_payment_status_returns_empty_queryset_when_no_match(self):
        self.create_order(payment_status=Order.PAYMENT_STATUS_CAPTURED)

        results = list_orders_by_payment_status(Order.PAYMENT_STATUS_FAILED)

        self.assertEqual(results.count(), 0)

    def test_list_orders_by_payment_status_returns_orders_ordered_by_created_at_desc(self):
        older = self.create_order(payment_status=Order.PAYMENT_STATUS_PENDING)
        newer = self.create_order(payment_status=Order.PAYMENT_STATUS_PENDING)

        results = list(list_orders_by_payment_status(Order.PAYMENT_STATUS_PENDING))

        self.assertEqual(results[0], newer)
        self.assertEqual(results[1], older)


class ListOrdersByShippingStatusSelectorTestCase(BaseSelectorFactoryMixin, TestCase):
    def test_list_orders_by_shipping_status_returns_only_matching_shipping_status(self):
        first_order = self.create_order(shipping_status=Order.SHIPPING_STATUS_PENDING)
        second_order = self.create_order(shipping_status=Order.SHIPPING_STATUS_PENDING)
        self.create_order(shipping_status=Order.SHIPPING_STATUS_DELIVERED)

        results = list(list_orders_by_shipping_status(Order.SHIPPING_STATUS_PENDING))

        self.assertEqual(len(results), 2)
        self.assertIn(first_order, results)
        self.assertIn(second_order, results)

    def test_list_orders_by_shipping_status_returns_empty_queryset_when_no_match(self):
        self.create_order(shipping_status=Order.SHIPPING_STATUS_SHIPPED)

        results = list_orders_by_shipping_status(Order.SHIPPING_STATUS_IN_TRANSIT)

        self.assertEqual(results.count(), 0)

    def test_list_orders_by_shipping_status_returns_orders_ordered_by_created_at_desc(self):
        older = self.create_order(shipping_status=Order.SHIPPING_STATUS_PENDING)
        newer = self.create_order(shipping_status=Order.SHIPPING_STATUS_PENDING)

        results = list(list_orders_by_shipping_status(Order.SHIPPING_STATUS_PENDING))

        self.assertEqual(results[0], newer)
        self.assertEqual(results[1], older)


class ListRecentOrdersSelectorTestCase(BaseSelectorFactoryMixin, TestCase):
    def test_list_recent_orders_returns_most_recent_orders(self):
        older = self.create_order()
        middle = self.create_order()
        newer = self.create_order()

        results = list(list_recent_orders(limit=2))

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], newer)
        self.assertEqual(results[1], middle)
        self.assertNotIn(older, results)

    def test_list_recent_orders_uses_default_limit_of_20(self):
        for _ in range(25):
            self.create_order()

        results = list(list_recent_orders())

        self.assertEqual(len(results), 20)

    def test_list_recent_orders_returns_empty_queryset_when_no_orders_exist(self):
        results = list(list_recent_orders())

        self.assertEqual(results, [])


class ListAllOrdersSelectorTestCase(BaseSelectorFactoryMixin, TestCase):
    def test_list_all_orders_returns_all_orders(self):
        first_order = self.create_order()
        second_order = self.create_order()

        results = list(list_all_orders())

        self.assertEqual(len(results), 2)
        self.assertIn(first_order, results)
        self.assertIn(second_order, results)

    def test_list_all_orders_returns_orders_ordered_by_created_at_desc(self):
        older = self.create_order()
        newer = self.create_order()

        results = list(list_all_orders())

        self.assertEqual(results[0], newer)
        self.assertEqual(results[1], older)

    def test_list_all_orders_returns_empty_queryset_when_no_orders_exist(self):
        results = list(list_all_orders())

        self.assertEqual(results, [])


class GetOrderForUpdateSelectorTestCase(BaseSelectorFactoryMixin, TestCase):
    def test_get_order_for_update_returns_order_when_found(self):
        order = self.create_full_order()

        with transaction.atomic():
            result = get_order_for_update(order.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, order.id)

    def test_get_order_for_update_returns_none_when_not_found(self):
        with transaction.atomic():
            result = get_order_for_update(uuid.uuid4())

        self.assertIsNone(result)

    def test_get_order_for_update_returns_related_data_accessibly(self):
        order = self.create_full_order()

        with transaction.atomic():
            result = get_order_for_update(order.id)

        self.assertEqual(result.customer, order.customer)
        self.assertEqual(result.totals.order, order)
        self.assertEqual(result.address.order, order)
        self.assertEqual(result.lifecycle.order, order)
        self.assertEqual(result.items.count(), 1)
        self.assertEqual(result.events.count(), 1)
        self.assertEqual(result.notes.count(), 1)


class ListOrdersForManagementSelectorTestCase(BaseSelectorFactoryMixin, TestCase):
    def test_list_orders_for_management_returns_all_orders(self):
        first_order = self.create_order()
        second_order = self.create_order()

        results = list(list_orders_for_management())

        self.assertEqual(len(results), 2)
        self.assertIn(first_order, results)
        self.assertIn(second_order, results)

    def test_list_orders_for_management_returns_orders_ordered_by_created_at_desc(self):
        older = self.create_order()
        newer = self.create_order()

        results = list(list_orders_for_management())

        self.assertEqual(results[0], newer)
        self.assertEqual(results[1], older)

    def test_list_orders_for_management_returns_empty_queryset_when_no_orders_exist(self):
        results = list(list_orders_for_management())

        self.assertEqual(results, [])


class GetOrderDetailForManagementSelectorTestCase(BaseSelectorFactoryMixin, TestCase):
    def test_get_order_detail_for_management_returns_order_when_found(self):
        order = self.create_full_order()

        result = get_order_detail_for_management(order.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, order.id)

    def test_get_order_detail_for_management_returns_none_when_not_found(self):
        result = get_order_detail_for_management(uuid.uuid4())

        self.assertIsNone(result)

    def test_get_order_detail_for_management_returns_related_data_accessibly(self):
        order = self.create_full_order()

        result = get_order_detail_for_management(order.id)

        self.assertEqual(result.customer, order.customer)
        self.assertEqual(result.totals.order, order)
        self.assertEqual(result.address.order, order)
        self.assertEqual(result.lifecycle.order, order)
        self.assertEqual(result.items.count(), 1)
        self.assertEqual(result.events.count(), 1)
        self.assertEqual(result.notes.count(), 1)