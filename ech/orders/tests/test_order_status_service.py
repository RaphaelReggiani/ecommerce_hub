import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.orders.constants.messages import (
    MSG_ERROR_ONLY_PENDING_ORDERS_CAN_BE_CONFIRMED,
    MSG_ERROR_ORDERS_MUST_BE_CONFIRMED,
    MSG_ERROR_ORDERS_MUST_BE_PROCESSING,
    MSG_ERROR_ORDERS_MUST_BE_SHIPPED,
)
from ech.orders.exceptions import InvalidOrderStatusTransitionError
from ech.orders.models import (
    Order,
    OrderLifecycle,
    OrderEvent,
)
from ech.orders.services.order_status_service import OrderStatusService


class BaseOrderStatusFactoryMixin:
    user_counter = 0

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


class ConfirmOrderServiceTestCase(BaseOrderStatusFactoryMixin, TestCase):
    def test_confirm_order_updates_order_status(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PENDING)

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.confirm_order()

        order.refresh_from_db()
        self.assertEqual(order.status, Order.ORDER_STATUS_CONFIRMED)

    def test_confirm_order_updates_lifecycle_confirmed_at(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PENDING)

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.confirm_order()

        order.refresh_from_db()
        self.assertIsNotNone(order.lifecycle.confirmed_at)

    def test_confirm_order_registers_confirmed_event(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PENDING)

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.confirm_order()

        event = order.events.first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, OrderEvent.TYPE_CONFIRMED)
        self.assertEqual(event.performed_by, performed_by)
        self.assertEqual(event.metadata, {})

    def test_confirm_order_raises_error_when_order_is_not_pending(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_CONFIRMED)

        service = OrderStatusService(order=order, performed_by=performed_by)

        with self.assertRaises(InvalidOrderStatusTransitionError) as context:
            service.confirm_order()

        self.assertEqual(
            str(context.exception),
            MSG_ERROR_ONLY_PENDING_ORDERS_CAN_BE_CONFIRMED,
        )

    def test_confirm_order_does_not_create_event_when_transition_is_invalid(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_CONFIRMED)

        service = OrderStatusService(order=order, performed_by=performed_by)

        with self.assertRaises(InvalidOrderStatusTransitionError):
            service.confirm_order()

        self.assertEqual(OrderEvent.objects.count(), 0)


class StartProcessingServiceTestCase(BaseOrderStatusFactoryMixin, TestCase):
    def test_start_processing_updates_order_status(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_CONFIRMED)

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.start_processing()

        order.refresh_from_db()
        self.assertEqual(order.status, Order.ORDER_STATUS_PROCESSING)

    def test_start_processing_updates_lifecycle_processing_at(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_CONFIRMED)

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.start_processing()

        order.refresh_from_db()
        self.assertIsNotNone(order.lifecycle.processing_at)

    def test_start_processing_registers_processing_started_event(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_CONFIRMED)

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.start_processing()

        event = order.events.first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, OrderEvent.TYPE_PROCESSING_STARTED)
        self.assertEqual(event.performed_by, performed_by)
        self.assertEqual(event.metadata, {})

    def test_start_processing_raises_error_when_order_is_not_confirmed(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PENDING)

        service = OrderStatusService(order=order, performed_by=performed_by)

        with self.assertRaises(InvalidOrderStatusTransitionError) as context:
            service.start_processing()

        self.assertEqual(
            str(context.exception),
            MSG_ERROR_ORDERS_MUST_BE_CONFIRMED,
        )

    def test_start_processing_does_not_create_event_when_transition_is_invalid(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PENDING)

        service = OrderStatusService(order=order, performed_by=performed_by)

        with self.assertRaises(InvalidOrderStatusTransitionError):
            service.start_processing()

        self.assertEqual(OrderEvent.objects.count(), 0)


class ShipOrderServiceTestCase(BaseOrderStatusFactoryMixin, TestCase):
    def test_ship_order_updates_order_status(self):
        performed_by = self.create_user()
        order = self.create_order(
            status=Order.ORDER_STATUS_PROCESSING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.ship_order()

        order.refresh_from_db()
        self.assertEqual(order.status, Order.ORDER_STATUS_SHIPPED)

    def test_ship_order_updates_shipping_status(self):
        performed_by = self.create_user()
        order = self.create_order(
            status=Order.ORDER_STATUS_PROCESSING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.ship_order()

        order.refresh_from_db()
        self.assertEqual(order.shipping_status, Order.SHIPPING_STATUS_SHIPPED)

    def test_ship_order_updates_lifecycle_shipped_at(self):
        performed_by = self.create_user()
        order = self.create_order(
            status=Order.ORDER_STATUS_PROCESSING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.ship_order()

        order.refresh_from_db()
        self.assertIsNotNone(order.lifecycle.shipped_at)

    def test_ship_order_registers_shipped_event(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PROCESSING)

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.ship_order()

        event = order.events.first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, OrderEvent.TYPE_SHIPPED)
        self.assertEqual(event.performed_by, performed_by)
        self.assertEqual(event.metadata, {})

    def test_ship_order_raises_error_when_order_is_not_processing(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_CONFIRMED)

        service = OrderStatusService(order=order, performed_by=performed_by)

        with self.assertRaises(InvalidOrderStatusTransitionError) as context:
            service.ship_order()

        self.assertEqual(
            str(context.exception),
            MSG_ERROR_ORDERS_MUST_BE_PROCESSING,
        )

    def test_ship_order_does_not_create_event_when_transition_is_invalid(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_CONFIRMED)

        service = OrderStatusService(order=order, performed_by=performed_by)

        with self.assertRaises(InvalidOrderStatusTransitionError):
            service.ship_order()

        self.assertEqual(OrderEvent.objects.count(), 0)


class DeliverOrderServiceTestCase(BaseOrderStatusFactoryMixin, TestCase):
    def test_deliver_order_updates_order_status(self):
        performed_by = self.create_user()
        order = self.create_order(
            status=Order.ORDER_STATUS_SHIPPED,
            shipping_status=Order.SHIPPING_STATUS_SHIPPED,
        )

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.deliver_order()

        order.refresh_from_db()
        self.assertEqual(order.status, Order.ORDER_STATUS_DELIVERED)

    def test_deliver_order_updates_shipping_status(self):
        performed_by = self.create_user()
        order = self.create_order(
            status=Order.ORDER_STATUS_SHIPPED,
            shipping_status=Order.SHIPPING_STATUS_SHIPPED,
        )

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.deliver_order()

        order.refresh_from_db()
        self.assertEqual(order.shipping_status, Order.SHIPPING_STATUS_DELIVERED)

    def test_deliver_order_updates_lifecycle_delivered_at(self):
        performed_by = self.create_user()
        order = self.create_order(
            status=Order.ORDER_STATUS_SHIPPED,
            shipping_status=Order.SHIPPING_STATUS_SHIPPED,
        )

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.deliver_order()

        order.refresh_from_db()
        self.assertIsNotNone(order.lifecycle.delivered_at)

    def test_deliver_order_registers_delivered_event(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_SHIPPED)

        service = OrderStatusService(order=order, performed_by=performed_by)
        service.deliver_order()

        event = order.events.first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, OrderEvent.TYPE_DELIVERED)
        self.assertEqual(event.performed_by, performed_by)
        self.assertEqual(event.metadata, {})

    def test_deliver_order_raises_error_when_order_is_not_shipped(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PROCESSING)

        service = OrderStatusService(order=order, performed_by=performed_by)

        with self.assertRaises(InvalidOrderStatusTransitionError) as context:
            service.deliver_order()

        self.assertEqual(
            str(context.exception),
            MSG_ERROR_ORDERS_MUST_BE_SHIPPED,
        )

    def test_deliver_order_does_not_create_event_when_transition_is_invalid(self):
        performed_by = self.create_user()
        order = self.create_order(status=Order.ORDER_STATUS_PROCESSING)

        service = OrderStatusService(order=order, performed_by=performed_by)

        with self.assertRaises(InvalidOrderStatusTransitionError):
            service.deliver_order()

        self.assertEqual(OrderEvent.objects.count(), 0)