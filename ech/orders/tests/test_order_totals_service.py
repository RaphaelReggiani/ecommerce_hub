from decimal import Decimal
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
)
from ech.orders.services.order_totals_service import OrderTotalsService
from ech.products.models import Product


class BaseOrderTotalsFactoryMixin:
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
            "discount_price": Decimal("80.00"),
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

    def create_order_item(self, **overrides):
        order = overrides.pop("order", self.create_order())
        product = overrides.pop("product", self.create_product())

        data = {
            "order": order,
            "product": product,
            "product_name_snapshot": "Test Product",
            "product_type_snapshot": Product.MOUSE,
            "brand_snapshot": "Test Brand",
            "quantity": 2,
            "unit_price": Decimal("100.00"),
            "discount_price": Decimal("80.00"),
            "total_price": Decimal("160.00"),
        }
        data.update(overrides)
        return OrderItem.objects.create(**data)


class OrderTotalsServiceTestCase(BaseOrderTotalsFactoryMixin, TestCase):

    def test_execute_creates_order_totals_when_it_does_not_exist(self):
        """Create OrderTotals when the order does not yet have totals."""
        order = self.create_order()
        self.create_order_item(
            order=order,
            quantity=2,
            unit_price=Decimal("100.00"),
            discount_price=Decimal("80.00"),
            total_price=Decimal("160.00"),
        )

        service = OrderTotalsService(order=order)
        service.execute()

        self.assertTrue(OrderTotals.objects.filter(order=order).exists())

        totals = OrderTotals.objects.get(order=order)
        self.assertEqual(totals.subtotal, Decimal("200.00"))
        self.assertEqual(totals.discount_total, Decimal("40.00"))
        self.assertEqual(totals.tax_total, Decimal("0.00"))
        self.assertEqual(totals.shipping_total, Decimal("0.00"))
        self.assertEqual(totals.grand_total, Decimal("160.00"))

    def test_execute_updates_existing_order_totals(self):
        """Update existing OrderTotals values when totals already exist."""
        order = self.create_order()
        self.create_order_item(
            order=order,
            quantity=1,
            unit_price=Decimal("100.00"),
            discount_price=Decimal("90.00"),
            total_price=Decimal("90.00"),
        )

        totals = OrderTotals.objects.create(
            order=order,
            subtotal=Decimal("999.00"),
            discount_total=Decimal("999.00"),
            tax_total=Decimal("999.00"),
            shipping_total=Decimal("999.00"),
            grand_total=Decimal("999.00"),
        )

        service = OrderTotalsService(order=order)
        service.execute()

        totals.refresh_from_db()
        self.assertEqual(totals.subtotal, Decimal("100.00"))
        self.assertEqual(totals.discount_total, Decimal("10.00"))
        self.assertEqual(totals.tax_total, Decimal("0.00"))
        self.assertEqual(totals.shipping_total, Decimal("0.00"))
        self.assertEqual(totals.grand_total, Decimal("90.00"))

    def test_execute_calculates_totals_correctly_for_single_discounted_item(self):
        """Calculate totals correctly for a single discounted order item."""
        order = self.create_order()
        self.create_order_item(
            order=order,
            quantity=3,
            unit_price=Decimal("120.00"),
            discount_price=Decimal("100.00"),
            total_price=Decimal("300.00"),
        )

        service = OrderTotalsService(order=order)
        service.execute()

        totals = OrderTotals.objects.get(order=order)
        self.assertEqual(totals.subtotal, Decimal("360.00"))
        self.assertEqual(totals.discount_total, Decimal("60.00"))
        self.assertEqual(totals.grand_total, Decimal("300.00"))

    def test_execute_calculates_totals_correctly_for_single_item_without_discount(self):
        """Calculate totals correctly for an item without discount."""
        order = self.create_order()
        self.create_order_item(
            order=order,
            quantity=2,
            unit_price=Decimal("75.00"),
            discount_price=None,
            total_price=Decimal("150.00"),
        )

        service = OrderTotalsService(order=order)
        service.execute()

        totals = OrderTotals.objects.get(order=order)
        self.assertEqual(totals.subtotal, Decimal("150.00"))
        self.assertEqual(totals.discount_total, Decimal("0.00"))
        self.assertEqual(totals.tax_total, Decimal("0.00"))
        self.assertEqual(totals.shipping_total, Decimal("0.00"))
        self.assertEqual(totals.grand_total, Decimal("150.00"))

    def test_execute_calculates_totals_correctly_for_multiple_items(self):
        """Calculate totals correctly when the order has multiple items."""
        order = self.create_order()

        self.create_order_item(
            order=order,
            quantity=2,
            unit_price=Decimal("100.00"),
            discount_price=Decimal("90.00"),
            total_price=Decimal("180.00"),
        )

        self.create_order_item(
            order=order,
            quantity=3,
            unit_price=Decimal("50.00"),
            discount_price=None,
            total_price=Decimal("150.00"),
        )

        service = OrderTotalsService(order=order)
        service.execute()

        totals = OrderTotals.objects.get(order=order)
        self.assertEqual(totals.subtotal, Decimal("350.00"))
        self.assertEqual(totals.discount_total, Decimal("20.00"))
        self.assertEqual(totals.tax_total, Decimal("0.00"))
        self.assertEqual(totals.shipping_total, Decimal("0.00"))
        self.assertEqual(totals.grand_total, Decimal("330.00"))

    def test_execute_sets_zero_totals_when_order_has_no_items(self):
        """Set all totals to zero when the order has no items."""
        order = self.create_order()

        service = OrderTotalsService(order=order)
        service.execute()

        totals = OrderTotals.objects.get(order=order)
        self.assertEqual(totals.subtotal, Decimal("0.00"))
        self.assertEqual(totals.discount_total, Decimal("0.00"))
        self.assertEqual(totals.tax_total, Decimal("0.00"))
        self.assertEqual(totals.shipping_total, Decimal("0.00"))
        self.assertEqual(totals.grand_total, Decimal("0.00"))

    def test_execute_does_not_accumulate_values_between_multiple_runs(self):
        """Ensure totals are recalculated and not accumulated between executions."""
        order = self.create_order()
        self.create_order_item(
            order=order,
            quantity=1,
            unit_price=Decimal("100.00"),
            discount_price=Decimal("80.00"),
            total_price=Decimal("80.00"),
        )

        service = OrderTotalsService(order=order)
        service.execute()
        service.execute()

        totals = OrderTotals.objects.get(order=order)
        self.assertEqual(totals.subtotal, Decimal("100.00"))
        self.assertEqual(totals.discount_total, Decimal("20.00"))
        self.assertEqual(totals.grand_total, Decimal("80.00"))

    def test_execute_recalculates_after_new_item_is_added(self):
        """Recalculate totals correctly after a new item is added to the order."""
        order = self.create_order()

        self.create_order_item(
            order=order,
            quantity=1,
            unit_price=Decimal("100.00"),
            discount_price=Decimal("90.00"),
            total_price=Decimal("90.00"),
        )

        service = OrderTotalsService(order=order)
        service.execute()

        self.create_order_item(
            order=order,
            quantity=2,
            unit_price=Decimal("50.00"),
            discount_price=None,
            total_price=Decimal("100.00"),
        )

        service.execute()

        totals = OrderTotals.objects.get(order=order)
        self.assertEqual(totals.subtotal, Decimal("200.00"))
        self.assertEqual(totals.discount_total, Decimal("10.00"))
        self.assertEqual(totals.tax_total, Decimal("0.00"))
        self.assertEqual(totals.shipping_total, Decimal("0.00"))
        self.assertEqual(totals.grand_total, Decimal("190.00"))

    def test_execute_keeps_tax_total_zero_in_current_logic(self):
        """Keep tax_total equal to zero according to current service logic."""
        order = self.create_order()
        self.create_order_item(
            order=order,
            quantity=1,
            unit_price=Decimal("100.00"),
            discount_price=Decimal("90.00"),
            total_price=Decimal("90.00"),
        )

        service = OrderTotalsService(order=order)
        service.execute()

        totals = OrderTotals.objects.get(order=order)
        self.assertEqual(totals.tax_total, Decimal("0.00"))

    def test_execute_keeps_shipping_total_zero_in_current_logic(self):
        """Keep shipping_total equal to zero according to current service logic."""
        order = self.create_order()
        self.create_order_item(
            order=order,
            quantity=1,
            unit_price=Decimal("100.00"),
            discount_price=Decimal("90.00"),
            total_price=Decimal("90.00"),
        )

        service = OrderTotalsService(order=order)
        service.execute()

        totals = OrderTotals.objects.get(order=order)
        self.assertEqual(totals.shipping_total, Decimal("0.00"))