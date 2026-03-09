from django.db import transaction

from ech.products.models import Product
from ech.products.exceptions import ProductOutOfStockError


@transaction.atomic
def decrease_inventory(*, product_id, quantity):
    """
    Safely decreases product inventory.

    Prevents race conditions during concurrent purchases.
    """

    product = (
        Product.objects
        .select_for_update()
        .get(id=product_id)
    )

    if product.inventory < quantity:
        raise ProductOutOfStockError()

    product.inventory -= quantity
    product.save(update_fields=["inventory"])

    return product