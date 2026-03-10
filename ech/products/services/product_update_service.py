from django.db import transaction

from ech.products.selectors import get_product_by_id
from ech.products.exceptions import ProductNotFoundError


@transaction.atomic
def update_product(*, product_id, **fields):

    product = get_product_by_id(product_id)

    if not product:
        raise ProductNotFoundError()

    for field, value in fields.items():
        setattr(product, field, value)

    product.save()

    return product