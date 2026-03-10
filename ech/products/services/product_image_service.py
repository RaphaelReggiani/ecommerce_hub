from django.db import transaction
from django.db.models import Max

from ech.products.models import ProductImage
from ech.products.selectors import get_product_by_id
from ech.products.exceptions import (
    ProductNotFoundError,
    ProductMaximumImagesError
)

from ech.products.constants.constants import (
    ProductImageRules,
)


@transaction.atomic
def add_product_image(*, product_id, images):
    """
    Adds one or multiple images to a product.

    This service ensures:
    - Product existence validation
    - Maximum image limit enforcement
    - Automatic sequential ordering
    - Atomic database operation
    - Efficient bulk insert
    """

    product = get_product_by_id(product_id)

    if not product:
        raise ProductNotFoundError()

    images_count = len(images)

    if images_count == 0:
        return []
    existing_images_count = ProductImage.objects.filter(
        product_id=product_id
    ).count()

    total_after_upload = existing_images_count + images_count

    if total_after_upload > ProductImageRules.MAX_IMAGES_ALLOWED:
        raise ProductMaximumImagesError(
            ProductImageRules.MAX_IMAGES_ALLOWED
        )

    last_order = (
        ProductImage.objects
        .filter(product_id=product_id)
        .aggregate(max_order=Max("order"))
        .get("max_order")
    )

    next_order = (last_order or 0) + 1

    product_images_to_create = []

    for index, image in enumerate(images):

        product_images_to_create.append(
            ProductImage(
                product=product,
                image=image,
                order=next_order + index,
            )
        )

    created_images = ProductImage.objects.bulk_create(
        product_images_to_create
    )

    return created_images


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