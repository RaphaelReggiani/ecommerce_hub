from django.db import transaction
from django.utils import timezone

from django.db.models import F
from ech.products.models import ProductInventory

from ech.orders.models import (
    Order,
    OrderEvent,
)

from ech.orders.selectors import get_order_for_update

from ech.orders.constants.messages import (
    MSG_ERROR_SHIPPED_OR_DELIVERED_ORDERS_CANNOT_BE_CANCELLED,
    MSG_ERROR_ORDER_ALREADY_CANCELLED,
)

from ech.orders.exceptions import (
    OrderCancellationNotAllowedError,
    OrderAlreadyCancelledError,
)


class CancelOrderService:
    """
    Service responsible for cancelling an order.

    Responsibilities:
    - Validate cancellation rules
    - Update order status
    - Update lifecycle timestamps
    - Register event
    """

    def __init__(self, *, order, performed_by):
        self.order = order
        self.performed_by = performed_by

    def execute(self):

        with transaction.atomic():

            self.order = get_order_for_update(self.order.id)

            self._validate_cancellation()

            now = timezone.now()

            self._restore_inventory()

            self._update_status(now)

            self._update_lifecycle(now)

            self._register_event()

    def _validate_cancellation(self):
        """
        Validates if the order can be cancelled.
        """

        if self.order.status in [
            Order.ORDER_STATUS_SHIPPED,
            Order.ORDER_STATUS_DELIVERED,
        ]:
            raise OrderCancellationNotAllowedError(
                MSG_ERROR_SHIPPED_OR_DELIVERED_ORDERS_CANNOT_BE_CANCELLED
            )

        if self.order.status == Order.ORDER_STATUS_CANCELLED:
            raise OrderAlreadyCancelledError(
                MSG_ERROR_ORDER_ALREADY_CANCELLED
            )

    def _update_status(self, now):
        """
        Updates order status to cancelled.
        """

        self.order.status = Order.ORDER_STATUS_CANCELLED
        self.order.updated_at = now

        self.order.save(update_fields=[
            "status",
            "updated_at",
        ])

    def _update_lifecycle(self, now):
        """
        Updates lifecycle cancellation timestamp.
        """

        lifecycle = self.order.lifecycle
        lifecycle.cancelled_at = now

        lifecycle.save(update_fields=[
            "cancelled_at",
        ])

    def _register_event(self):
        """
        Registers cancellation event.
        """

        OrderEvent.objects.create(
            order=self.order,
            event_type=OrderEvent.TYPE_CANCELLED,
            performed_by=self.performed_by,
            metadata={
                "reason": "manual_cancellation"
            }
        )

    def _restore_inventory(self):
        """
        Restores inventory quantities for all cancelled order items.
        """

        for item in self.order.items.select_related("product").only(
            "product",
            "quantity",
        ).all():

            inventory = (
                ProductInventory.objects
                .select_for_update()
                .filter(product=item.product)
                .first()
            )

            if inventory:
                inventory.quantity = F("quantity") + item.quantity
                inventory.save(update_fields=["quantity", "updated_at"])


