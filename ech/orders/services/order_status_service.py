from django.db import transaction
from django.utils import timezone

from ech.orders.selectors import get_order_for_update

from ech.orders.models import (
    Order,
    OrderEvent,
)

from ech.orders.constants.messages import (
    MSG_ERROR_ONLY_PENDING_ORDERS_CAN_BE_CONFIRMED,
    MSG_ERROR_ORDERS_MUST_BE_CONFIRMED,
    MSG_ERROR_ORDERS_MUST_BE_PROCESSING,
    MSG_ERROR_ORDERS_MUST_BE_SHIPPED,
)

from ech.orders.exceptions import (
    InvalidOrderStatusTransitionError,
)


class OrderStatusService:
    """
    Service responsible for managing order status transitions.
    """

    def __init__(self, *, order, performed_by):
        self.order = order
        self.performed_by = performed_by

    def confirm_order(self):

        with transaction.atomic():

            now = timezone.now()

            self.order = get_order_for_update(self.order.id)

            if self.order.status != Order.ORDER_STATUS_PENDING:
                raise InvalidOrderStatusTransitionError(
                    MSG_ERROR_ONLY_PENDING_ORDERS_CAN_BE_CONFIRMED
                )

            self.order.status = Order.ORDER_STATUS_CONFIRMED
            self.order.updated_at = now
            self.order.save(update_fields=["status", "updated_at"])

            lifecycle = self.order.lifecycle
            lifecycle.confirmed_at = now
            lifecycle.save(update_fields=["confirmed_at"])

            self._register_event(OrderEvent.TYPE_CONFIRMED)

    def start_processing(self):

        with transaction.atomic():

            now = timezone.now()

            self.order = get_order_for_update(self.order.id)

            if self.order.status != Order.ORDER_STATUS_CONFIRMED:
                raise InvalidOrderStatusTransitionError(
                    MSG_ERROR_ORDERS_MUST_BE_CONFIRMED
                )

            self.order.status = Order.ORDER_STATUS_PROCESSING
            self.order.updated_at = now
            self.order.save(update_fields=["status", "updated_at"])

            lifecycle = self.order.lifecycle
            lifecycle.processing_at = now
            lifecycle.save(update_fields=["processing_at"])

            self._register_event(OrderEvent.TYPE_PROCESSING_STARTED)

    def ship_order(self):

        with transaction.atomic():

            now = timezone.now()

            self.order = get_order_for_update(self.order.id)

            if self.order.status != Order.ORDER_STATUS_PROCESSING:
                raise InvalidOrderStatusTransitionError(
                    MSG_ERROR_ORDERS_MUST_BE_PROCESSING
                )

            self.order.status = Order.ORDER_STATUS_SHIPPED
            self.order.shipping_status = Order.SHIPPING_STATUS_SHIPPED
            self.order.updated_at = now
            self.order.save(update_fields=[
                "status",
                "shipping_status",
                "updated_at",
            ])

            lifecycle = self.order.lifecycle
            lifecycle.shipped_at = now
            lifecycle.save(update_fields=["shipped_at"])

            self._register_event(OrderEvent.TYPE_SHIPPED)

    def deliver_order(self):

        with transaction.atomic():

            now = timezone.now()

            self.order = get_order_for_update(self.order.id)

            if self.order.status != Order.ORDER_STATUS_SHIPPED:
                raise InvalidOrderStatusTransitionError(
                    MSG_ERROR_ORDERS_MUST_BE_SHIPPED
                )

            self.order.status = Order.ORDER_STATUS_DELIVERED
            self.order.shipping_status = Order.SHIPPING_STATUS_DELIVERED
            self.order.updated_at = now
            self.order.save(update_fields=[
                "status",
                "shipping_status",
                "updated_at",
            ])

            lifecycle = self.order.lifecycle
            lifecycle.delivered_at = now
            lifecycle.save(update_fields=["delivered_at"])

            self._register_event(OrderEvent.TYPE_DELIVERED)

    def _register_event(self, event_type):

        OrderEvent.objects.create(
            order=self.order,
            event_type=event_type,
            performed_by=self.performed_by,
            metadata={},
        )

