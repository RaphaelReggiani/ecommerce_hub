from django.db import transaction

from ech.products.domain_events.dispatcher import EventDispatcher
from ech.products.domain_events.events import ProductDeletedEvent
from ech.products.exceptions import ProductNotFoundError
from ech.products.selectors import get_product_by_id


@transaction.atomic
def delete_product(*, product_id, performed_by=None):
    """
    Soft deletes a product and dispatches the corresponding domain event.
    """

    product = get_product_by_id(product_id)

    if not product:
        raise ProductNotFoundError()

    product.is_active = False
    product.save(update_fields=["is_active"])

    EventDispatcher.dispatch(
        ProductDeletedEvent(
            product=product,
            performed_by=performed_by,
        )
    )

    return product