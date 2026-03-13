from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
    OrderLifecycle,
    OrderEvent,
)

from ech.products.selectors import get_active_product_by_id


class CreateOrderService:
    """
    Service responsible for creating an order and all related entities.

    Responsibilities:
    - Validate products
    - Create Order
    - Create OrderItems
    - Calculate totals
    - Create lifecycle
    - Register order event
    """

    def __init__(self, *, customer, items, idempotency_key=None):
        """
        Parameters
        ----------

        customer:
            User instance placing the order

        items:
            List of dicts:

            [
                {
                    "product_id": int,
                    "quantity": int
                }
            ]
        """

        self.customer = customer
        self.items = items
        self.idempotency_key = idempotency_key

        self.order = None

        self.subtotal = Decimal("0.00")
        self.discount_total = Decimal("0.00")

    def execute(self):
        """
        Creates the order and all related records.
        """

        if self.idempotency_key:

            existing_order = Order.objects.filter(
                idempotency_key=self.idempotency_key
            ).first()

            if existing_order:
                return existing_order

        with transaction.atomic():

            self._create_order()

            self._create_items()

            self._create_totals()

            self._create_lifecycle()

            self._register_event()

        return self.order

    def _create_order(self):

        self.order = Order.objects.create(
            customer=self.customer,
            idempotency_key=self.idempotency_key,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

    def _create_items(self):

        for item in self.items:

            product = get_active_product_by_id(item["product_id"])

            if not product:
                raise ValueError("Product not available")

            quantity = int(item["quantity"])

            unit_price = product.price
            discount_price = product.discount_price

            final_price = discount_price or unit_price

            total_price = final_price * quantity

            self.subtotal += unit_price * quantity

            if discount_price:
                self.discount_total += (unit_price - discount_price) * quantity

            OrderItem.objects.create(
                order=self.order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                discount_price=discount_price,
                total_price=total_price,

                product_name_snapshot=product.name,
                brand_snapshot=product.brand,
                product_type_snapshot=product.product_type,
            )

    def _create_totals(self):

        tax_total = Decimal("0.00")
        shipping_total = Decimal("0.00")

        grand_total = (
            self.subtotal
            - self.discount_total
            + tax_total
            + shipping_total
        )

        OrderTotals.objects.create(
            order=self.order,
            subtotal=self.subtotal,
            discount_total=self.discount_total,
            tax_total=tax_total,
            shipping_total=shipping_total,
            grand_total=grand_total,
        )

    def _create_lifecycle(self):

        OrderLifecycle.objects.create(
            order=self.order,
            confirmed_at=None,
            processing_at=None,
            shipped_at=None,
            delivered_at=None,
            cancelled_at=None,
            refunded_at=None,
        )

    def _register_event(self):

        OrderEvent.objects.create(
            order=self.order,
            event_type=OrderEvent.TYPE_CREATED,
            performed_by=self.customer,
            metadata={
                "created_at": timezone.now().isoformat()
            }
        )