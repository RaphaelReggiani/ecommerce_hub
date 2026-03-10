from django.db import transaction

from ech.products.selectors import get_product_by_id
from ech.products.exceptions import ProductNotFoundError


@transaction.atomic
def delete_product(*, product_id):

    product = get_product_by_id(product_id)

    if not product:
        raise ProductNotFoundError()

    product.is_active = False
    product.save(update_fields=["is_active"])

    return product