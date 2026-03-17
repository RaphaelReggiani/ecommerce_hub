from django.contrib.auth import get_user_model
from django.test import TestCase
import uuid
from django.core.cache import cache

from ech.orders.models import Order, OrderLifecycle, OrderEvent
from ech.orders.domain_events.dispatcher import EventDispatcher
from ech.orders.domain_events.events import (
    OrderConfirmedEvent,
    OrderCancelledEvent,
)
from ech.orders.domain_events.handlers import (
    handle_order_confirmed_event,
    handle_order_cancelled_event,
)
from ech.orders.domain_events.registry import register_order_event_handlers


class DomainEventsTestCase(TestCase):
    def create_user(self):
        User = get_user_model()
        unique_suffix = uuid.uuid4().hex[:8]
        email = f"user_{unique_suffix}@test.com"

        return User.objects.create_user(
            email=email,
            user_name=f"Test User {unique_suffix}",
            password="StrongPass123!",
        )

    def create_order(self):
        order = Order.objects.create(
            customer=self.create_user(),
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )
        OrderLifecycle.objects.create(order=order)
        return order

    def setUp(self):
        cache.clear()
        EventDispatcher.clear()
        EventDispatcher.register(OrderConfirmedEvent, handle_order_confirmed_event)
        EventDispatcher.register(OrderCancelledEvent, handle_order_cancelled_event)

    def tearDown(self):
        EventDispatcher.clear()
        register_order_event_handlers()

    def test_dispatch_calls_registered_handler(self):
        order = self.create_order()
        performed_by = self.create_user()

        EventDispatcher.dispatch(
            OrderConfirmedEvent(order=order, performed_by=performed_by)
        )

        self.assertEqual(OrderEvent.objects.count(), 1)
        event = OrderEvent.objects.first()
        self.assertEqual(event.event_type, OrderEvent.TYPE_CONFIRMED)

    def test_dispatch_cancelled_event_creates_cancelled_order_event(self):
        order = self.create_order()
        performed_by = self.create_user()

        EventDispatcher.dispatch(
            OrderCancelledEvent(
                order=order,
                performed_by=performed_by,
                reason="manual_cancellation",
            )
        )

        event = OrderEvent.objects.first()
        self.assertEqual(event.event_type, OrderEvent.TYPE_CANCELLED)
        self.assertEqual(event.metadata, {"reason": "manual_cancellation"})