from django.db import transaction

from ech.products.models import ProductInventory

from ech.products.constants.messages import (
    MSG_ERROR_STOCK_NOT_ENOUGH_STOCK_AVAILABLE,
)


class OutOfStockError(Exception):
    """
    Raised when there is not enough stock to complete the operation.
    """
    pass


def get_available_stock(product_id):
    """
    Returns available stock for a product.
    """

    inventory = ProductInventory.objects.get(product_id=product_id)

    return inventory.quantity


def reserve_stock(product_id, quantity):
    """
    Reserves stock for a product using row-level locking.
    Prevents overselling under concurrent requests.
    """

    with transaction.atomic():

        inventory = (
            ProductInventory.objects
            .select_for_update()
            .get(product_id=product_id)
        )

        if inventory.quantity < quantity:
            raise OutOfStockError(MSG_ERROR_STOCK_NOT_ENOUGH_STOCK_AVAILABLE)

        inventory.quantity -= quantity

        inventory.save(update_fields=["quantity"])

        return inventory


def release_stock(product_id, quantity):
    """
    Releases previously reserved stock.
    Useful for cancelled orders or failed payments.
    """

    with transaction.atomic():

        inventory = (
            ProductInventory.objects
            .select_for_update()
            .get(product_id=product_id)
        )

        inventory.quantity += quantity

        inventory.save(update_fields=["quantity"])

        return inventory