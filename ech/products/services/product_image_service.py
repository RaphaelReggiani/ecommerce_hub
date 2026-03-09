from django.db import transaction

from ech.products.models import ProductImage
from ech.products.selectors import get_product_by_id
from ech.products.exceptions import (
    ProductNotFoundError,
)

from ech.products.constants.constants import (
    ProductImageRules,
)


@transaction.atomic
def add_product_image(*, product_id, images):
    """
    Adds images to a product.

    Images are uploaded via:
    POST /products/{id}/images/

    Parameters
    ----------
    product_id : int
    images : list[File]

    Returns
    -------
    list[ProductImage]
    """

    product = get_product_by_id(product_id)

    if not product:
        raise ProductNotFoundError()

    existing_images_count = product.images.count()

    new_images = []

    current_order = existing_images_count + 1

    for image in images:

        product_image = ProductImage.objects.create(
            product=product,
            image=image,
            order=current_order
        )

        new_images.append(product_image)

        current_order += 1

    return new_images


def validate_product_minimum_images(product):
    """
    Validates if the product has the minimum required number of images.
    This should be called when activating the product or before publishing.
    """

    images_count = product.images.count()

    if images_count < ProductImageRules.MIN_IMAGES_REQUIRED:
        from ech.products.exceptions import ProductMinimumImagesError

        raise ProductMinimumImagesError(
            ProductImageRules.MIN_IMAGES_REQUIRED
        )