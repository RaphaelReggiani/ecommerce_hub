from decimal import Decimal
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.orders.constants.messages import (
    MSG_ERROR_SHIPPED_OR_DELIVERED_ORDERS_CANNOT_BE_CANCELLED,
    MSG_ERROR_ORDER_ALREADY_CANCELLED,
)
from ech.orders.exceptions import (
    OrderCancellationNotAllowedError,
    OrderAlreadyCancelledError,
)
from ech.orders.models import (
    Order,
    OrderItem,
    OrderLifecycle,
    OrderEvent,
)
from ech.orders.services.order_cancel_service import CancelOrderService
from ech.products.models import Product, ProductInventory


class BaseCancelOrderFactoryMixin:
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

    def create_inventory(self, product, quantity=10):
        return ProductInventory.objects.create(
            product=product,
            quantity=quantity,
        )

    def create_order(self, **overrides):
        data = {
            "customer": self.create_user(),
            "status": Order.ORDER_STATUS_PENDING,
            "payment_status": Order.PAYMENT_STATUS_PENDING,
            "shipping_status": Order.SHIPPING_STATUS_PENDING,
            "currency": "USD",
        }
        data.update(overrides)
        order = Order.objects.create(**data)

        OrderLifecycle.objects.create(order=order)
        return order

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


class CancelOrderServiceTestCase(BaseCancelOrderFactoryMixin, TestCase):
    def test_execute_cancels_order_successfully(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PENDING)

        service = CancelOrderService(order=order, performed_by=performed_by)
        service.execute()

        order.refresh_from_db()
        self.assertEqual(order.status, Order.ORDER_STATUS_CANCELLED)

    def test_execute_updates_lifecycle_cancelled_at(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PENDING)

        service = CancelOrderService(order=order, performed_by=performed_by)
        service.execute()

        order.refresh_from_db()
        self.assertIsNotNone(order.lifecycle.cancelled_at)

    def test_execute_registers_cancelled_event(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PENDING)

        service = CancelOrderService(order=order, performed_by=performed_by)
        service.execute()

        event = order.events.first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, OrderEvent.TYPE_CANCELLED)
        self.assertEqual(event.performed_by, performed_by)
        self.assertEqual(event.metadata, {"reason": "manual_cancellation"})

    def test_execute_restores_inventory_for_single_item(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PENDING)

        product = self.create_product()
        inventory = self.create_inventory(product=product, quantity=3)

        self.create_order_item(
            order=order,
            product=product,
            quantity=2,
        )

        service = CancelOrderService(order=order, performed_by=performed_by)
        service.execute()

        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, 5)

    def test_execute_restores_inventory_for_multiple_items(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PENDING)

        product_1 = self.create_product()
        product_2 = self.create_product()

        inventory_1 = self.create_inventory(product=product_1, quantity=5)
        inventory_2 = self.create_inventory(product=product_2, quantity=7)

        self.create_order_item(order=order, product=product_1, quantity=2)
        self.create_order_item(order=order, product=product_2, quantity=4)

        service = CancelOrderService(order=order, performed_by=performed_by)
        service.execute()

        inventory_1.refresh_from_db()
        inventory_2.refresh_from_db()

        self.assertEqual(inventory_1.quantity, 7)
        self.assertEqual(inventory_2.quantity, 11)

    def test_execute_does_not_fail_when_product_inventory_does_not_exist(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PENDING)

        product = self.create_product()

        self.create_order_item(
            order=order,
            product=product,
            quantity=2,
        )

        service = CancelOrderService(order=order, performed_by=performed_by)
        service.execute()

        order.refresh_from_db()
        self.assertEqual(order.status, Order.ORDER_STATUS_CANCELLED)
        self.assertEqual(OrderEvent.objects.count(), 1)

    def test_execute_raises_order_cancellation_not_allowed_error_for_shipped_order(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_SHIPPED)

        service = CancelOrderService(order=order, performed_by=performed_by)

        with self.assertRaises(OrderCancellationNotAllowedError) as context:
            service.execute()

        self.assertEqual(
            str(context.exception),
            MSG_ERROR_SHIPPED_OR_DELIVERED_ORDERS_CANNOT_BE_CANCELLED,
        )

    def test_execute_raises_order_cancellation_not_allowed_error_for_delivered_order(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_DELIVERED)

        service = CancelOrderService(order=order, performed_by=performed_by)

        with self.assertRaises(OrderCancellationNotAllowedError) as context:
            service.execute()

        self.assertEqual(
            str(context.exception),
            MSG_ERROR_SHIPPED_OR_DELIVERED_ORDERS_CANNOT_BE_CANCELLED,
        )

    def test_execute_raises_order_already_cancelled_error_for_cancelled_order(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_CANCELLED)

        service = CancelOrderService(order=order, performed_by=performed_by)

        with self.assertRaises(OrderAlreadyCancelledError) as context:
            service.execute()

        self.assertEqual(
            str(context.exception),
            MSG_ERROR_ORDER_ALREADY_CANCELLED,
        )

    def test_execute_does_not_create_event_when_order_is_shipped(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_SHIPPED)

        service = CancelOrderService(order=order, performed_by=performed_by)

        with self.assertRaises(OrderCancellationNotAllowedError):
            service.execute()

        self.assertEqual(OrderEvent.objects.count(), 0)

    def test_execute_does_not_create_event_when_order_is_delivered(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_DELIVERED)

        service = CancelOrderService(order=order, performed_by=performed_by)

        with self.assertRaises(OrderCancellationNotAllowedError):
            service.execute()

        self.assertEqual(OrderEvent.objects.count(), 0)

    def test_execute_does_not_create_event_when_order_is_already_cancelled(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_CANCELLED)

        service = CancelOrderService(order=order, performed_by=performed_by)

        with self.assertRaises(OrderAlreadyCancelledError):
            service.execute()

        self.assertEqual(OrderEvent.objects.count(), 0)

    def test_execute_does_not_change_status_when_order_is_shipped(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_SHIPPED)

        service = CancelOrderService(order=order, performed_by=performed_by)

        with self.assertRaises(OrderCancellationNotAllowedError):
            service.execute()

        order.refresh_from_db()
        self.assertEqual(order.status, Order.ORDER_STATUS_SHIPPED)

    def test_execute_does_not_change_status_when_order_is_delivered(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_DELIVERED)

        service = CancelOrderService(order=order, performed_by=performed_by)

        with self.assertRaises(OrderCancellationNotAllowedError):
            service.execute()

        order.refresh_from_db()
        self.assertEqual(order.status, Order.ORDER_STATUS_DELIVERED)

    def test_execute_does_not_update_lifecycle_when_cancellation_is_invalid(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_SHIPPED)

        service = CancelOrderService(order=order, performed_by=performed_by)

        with self.assertRaises(OrderCancellationNotAllowedError):
            service.execute()

        order.refresh_from_db()
        self.assertIsNone(order.lifecycle.cancelled_at)

    def test_execute_does_not_restore_inventory_when_cancellation_is_invalid(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_SHIPPED)

        product = self.create_product()
        inventory = self.create_inventory(product=product, quantity=4)

        self.create_order_item(
            order=order,
            product=product,
            quantity=3,
        )

        service = CancelOrderService(order=order, performed_by=performed_by)

        with self.assertRaises(OrderCancellationNotAllowedError):
            service.execute()

        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, 4)