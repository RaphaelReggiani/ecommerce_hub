from decimal import Decimal

from django.db import transaction

from ech.orders.models import OrderTotals


class OrderTotalsService:
    """
    Service responsible for recalculating order totals
    based on its OrderItems.
    """

    def __init__(self, *, order):
        self.order = order

        self.subtotal = Decimal("0.00")
        self.discount_total = Decimal("0.00")
        self.tax_total = Decimal("0.00")
        self.shipping_total = Decimal("0.00")

    def execute(self):
        """
        Recalculate totals and update OrderTotals record.
        """

        self.subtotal = Decimal("0.00")
        self.discount_total = Decimal("0.00")
        self.tax_total = Decimal("0.00")
        self.shipping_total = Decimal("0.00")

        with transaction.atomic():

            self._calculate_items()

            self._calculate_extras()

            self._save_totals()

    def _calculate_items(self):
        """
        Calculates subtotal and discount totals from order items.
        """

        items = self.order.items.all().only(
            "unit_price",
            "discount_price",
            "quantity"
        )

        for item in items:

            unit_price = item.unit_price
            discount_price = item.discount_price
            quantity = item.quantity

            self.subtotal += unit_price * quantity

            if discount_price is not None:
                self.discount_total += (unit_price - discount_price) * quantity

    def _calculate_extras(self):
        """
        Calculates taxes and shipping.
        Currently static but easily replaceable by real logic.
        """

        self.tax_total = Decimal("0.00")
        self.shipping_total = Decimal("0.00")

    def _save_totals(self):
        """
        Saves totals into OrderTotals.
        """

        grand_total = (
            self.subtotal
            - self.discount_total
            + self.tax_total
            + self.shipping_total
        )

        totals, _ = OrderTotals.objects.get_or_create(
            order=self.order
        )

        totals.subtotal = self.subtotal
        totals.discount_total = self.discount_total
        totals.tax_total = self.tax_total
        totals.shipping_total = self.shipping_total
        totals.grand_total = grand_total

        totals.save(update_fields=[
            "subtotal",
            "discount_total",
            "tax_total",
            "shipping_total",
            "grand_total",
            "updated_at",
        ])

