from django.db import transaction

from ech.products.models import ProductInventory
from ech.products.exceptions import ProductOutOfStockError


@transaction.atomic
def decrease_inventory(*, product_id, quantity):

    inventory = (
        ProductInventory.objects
        .select_for_update()
        .get(product_id=product_id)
    )

    if inventory.quantity < quantity:
        raise ProductOutOfStockError()

    inventory.quantity -= quantity
    inventory.save(update_fields=["quantity"])

    return inventory