from django.db import transaction

from ech.products.domain_events.dispatcher import EventDispatcher
from ech.products.domain_events.events import ProductUpdatedEvent
from ech.products.exceptions import ProductNotFoundError
from ech.products.selectors import get_product_by_id


@transaction.atomic
def update_product(*, product_id, performed_by=None, **fields):
    """
    Updates a product and dispatches the corresponding domain event.
    """

    product = get_product_by_id(product_id)

    if not product:
        raise ProductNotFoundError()

    if not fields:
        return product

    for field, value in fields.items():
        setattr(product, field, value)

    product.save()

    EventDispatcher.dispatch(
        ProductUpdatedEvent(
            product=product,
            performed_by=performed_by,
        )
    )

    return product