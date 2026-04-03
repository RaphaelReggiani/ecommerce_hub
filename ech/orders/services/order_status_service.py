from django.db import transaction
from django.utils import timezone

from ech.orders.selectors import get_order_for_update

from ech.orders.services.cache_service import invalidate_order_related_caches
from ech.orders.services.order_log_service import OrderLogService

from ech.orders.models import (
    Order,
)

from ech.orders.domain_events.dispatcher import EventDispatcher
from ech.orders.domain_events.events import (
    OrderConfirmedEvent,
    OrderProcessingStartedEvent,
    OrderShippedEvent,
    OrderDeliveredEvent,
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
                OrderLogService.log_invalid_status_transition(
                    order=self.order,
                    attempted_action="confirm_order",
                    performed_by=self.performed_by,
                    reason=MSG_ERROR_ONLY_PENDING_ORDERS_CAN_BE_CONFIRMED,
                )
                raise InvalidOrderStatusTransitionError(
                    MSG_ERROR_ONLY_PENDING_ORDERS_CAN_BE_CONFIRMED
                )

            previous_status = self.order.status

            self.order.status = Order.ORDER_STATUS_CONFIRMED
            self.order.updated_at = now
            self.order.save(update_fields=["status", "updated_at"])

            lifecycle = self.order.lifecycle
            lifecycle.confirmed_at = now
            lifecycle.save(update_fields=["confirmed_at"])

            EventDispatcher.dispatch(
                OrderConfirmedEvent(
                    order=self.order,
                    performed_by=self.performed_by,
                )
            )

        invalidate_order_related_caches(self.order)

        OrderLogService.log_order_confirmed(
            order=self.order,
            performed_by=self.performed_by,
            metadata={
                "previous_status": previous_status,
                "new_status": self.order.status,
                "confirmed_at": lifecycle.confirmed_at,
            },
        )

        return self.order

    def start_processing(self):
        with transaction.atomic():
            now = timezone.now()

            self.order = get_order_for_update(self.order.id)

            if self.order.status != Order.ORDER_STATUS_CONFIRMED:
                OrderLogService.log_invalid_status_transition(
                    order=self.order,
                    attempted_action="start_processing",
                    performed_by=self.performed_by,
                    reason=MSG_ERROR_ORDERS_MUST_BE_CONFIRMED,
                )
                raise InvalidOrderStatusTransitionError(
                    MSG_ERROR_ORDERS_MUST_BE_CONFIRMED
                )

            previous_status = self.order.status

            self.order.status = Order.ORDER_STATUS_PROCESSING
            self.order.updated_at = now
            self.order.save(update_fields=["status", "updated_at"])

            lifecycle = self.order.lifecycle
            lifecycle.processing_at = now
            lifecycle.save(update_fields=["processing_at"])

            EventDispatcher.dispatch(
                OrderProcessingStartedEvent(
                    order=self.order,
                    performed_by=self.performed_by,
                )
            )

        invalidate_order_related_caches(self.order)

        OrderLogService.log_order_processing_started(
            order=self.order,
            performed_by=self.performed_by,
            metadata={
                "previous_status": previous_status,
                "new_status": self.order.status,
                "processing_at": lifecycle.processing_at,
            },
        )

        return self.order

    def ship_order(self):
        with transaction.atomic():
            now = timezone.now()

            self.order = get_order_for_update(self.order.id)

            if self.order.status != Order.ORDER_STATUS_PROCESSING:
                OrderLogService.log_invalid_status_transition(
                    order=self.order,
                    attempted_action="ship_order",
                    performed_by=self.performed_by,
                    reason=MSG_ERROR_ORDERS_MUST_BE_PROCESSING,
                )
                raise InvalidOrderStatusTransitionError(
                    MSG_ERROR_ORDERS_MUST_BE_PROCESSING
                )

            previous_status = self.order.status
            previous_shipping_status = self.order.shipping_status

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

            EventDispatcher.dispatch(
                OrderShippedEvent(
                    order=self.order,
                    performed_by=self.performed_by,
                )
            )

        invalidate_order_related_caches(self.order)

        OrderLogService.log_order_shipped(
            order=self.order,
            performed_by=self.performed_by,
            metadata={
                "previous_status": previous_status,
                "new_status": self.order.status,
                "previous_shipping_status": previous_shipping_status,
                "new_shipping_status": self.order.shipping_status,
                "shipped_at": lifecycle.shipped_at,
            },
        )

        return self.order

    def deliver_order(self):
        with transaction.atomic():
            now = timezone.now()

            self.order = get_order_for_update(self.order.id)

            if self.order.status != Order.ORDER_STATUS_SHIPPED:
                OrderLogService.log_invalid_status_transition(
                    order=self.order,
                    attempted_action="deliver_order",
                    performed_by=self.performed_by,
                    reason=MSG_ERROR_ORDERS_MUST_BE_SHIPPED,
                )
                raise InvalidOrderStatusTransitionError(
                    MSG_ERROR_ORDERS_MUST_BE_SHIPPED
                )

            previous_status = self.order.status
            previous_shipping_status = self.order.shipping_status

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

            EventDispatcher.dispatch(
                OrderDeliveredEvent(
                    order=self.order,
                    performed_by=self.performed_by,
                )
            )

        invalidate_order_related_caches(self.order)

        OrderLogService.log_order_delivered(
            order=self.order,
            performed_by=self.performed_by,
            metadata={
                "previous_status": previous_status,
                "new_status": self.order.status,
                "previous_shipping_status": previous_shipping_status,
                "new_shipping_status": self.order.shipping_status,
                "delivered_at": lifecycle.delivered_at,
            },
        )

        return self.order

    @staticmethod
    def update_order_payment_status(*, order_id, payment_status):
        with transaction.atomic():
            now = timezone.now()

            order = get_order_for_update(order_id)
            previous_payment_status = order.payment_status

            order.payment_status = payment_status
            order.updated_at = now
            order.save(update_fields=["payment_status", "updated_at"])

        invalidate_order_related_caches(order)

        OrderLogService.log_payment_status_updated(
            order=order,
            previous_status=previous_payment_status,
            new_status=order.payment_status,
            metadata={
                "updated_at": order.updated_at,
            },
        )

        return order


