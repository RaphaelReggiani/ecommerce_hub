from django.db import transaction

from ech.products.exceptions import ProductOutOfStockError
from ech.products.models import ProductInventory
from ech.products.utils.cache_keys import (
    invalidate_product_cache,
    invalidate_product_list_cache,
)


@transaction.atomic
def decrease_inventory(*, product_id, quantity):
    """
    Decreases product inventory using row-level locking.

    This service ensures:
    - concurrency-safe stock updates
    - out-of-stock validation
    - cache invalidation after inventory mutation
    """

    inventory = (
        ProductInventory.objects
        .select_for_update()
        .get(product_id=product_id)
    )

    if inventory.quantity < quantity:
        raise ProductOutOfStockError()

    inventory.quantity -= quantity
    inventory.save(update_fields=["quantity"])

    invalidate_product_cache(product_id)
    invalidate_product_list_cache()

    return inventory