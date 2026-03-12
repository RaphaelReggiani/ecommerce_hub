from django.db import transaction

from ech.products.models import (
    Product, 
    ProductInventory,
)

from ech.products.exceptions import (
    ProductCreationPermissionDeniedError,
    InvalidProductTypeError,
    InvalidProductPriceError,
    InvalidDiscountPriceError,
    InvalidInventoryValueError,
)

from ech.products.constants.roles_management import (
    ALLOWED_PRODUCTS_ROLES,
)


@transaction.atomic
def create_product(
    *,
    user,
    name,
    product_type,
    brand,
    description,
    technical_information,
    price,
    discount_price=None,
    inventory=0,
):
    """
    Creates a new product.

    Images are uploaded in a second step via:
    POST /products/{id}/images/

    Only Operations Staff, Admin and SuperAdmin can create products.
    """

    _validate_user_permission(user)

    _validate_product_type(product_type)

    _validate_price(price)

    _validate_discount(price, discount_price)

    _validate_inventory(inventory)

    product = Product.objects.create(
        name=name,
        product_type=product_type,
        brand=brand,
        sold_by=user,
        description=description,
        technical_information=technical_information,
        price=price,
        discount_price=discount_price,
    )

    ProductInventory.objects.create(
        product=product,
        quantity=inventory
    )

    return product


def _validate_user_permission(user):
    """
    Validates if the user has permission to create products.
    """

    if user.user_role not in ALLOWED_PRODUCTS_ROLES:
        raise ProductCreationPermissionDeniedError()


def _validate_product_type(product_type):
    """
    Validates if the product type is valid.
    """

    valid_types = {choice[0] for choice in Product.PRODUCT_CHOICES}

    if product_type not in valid_types:
        raise InvalidProductTypeError()


def _validate_price(price):
    """
    Validates product price.
    """

    if price is None or price <= 0:
        raise InvalidProductPriceError()


def _validate_discount(price, discount_price):
    """
    Validates discount price logic.
    """

    if discount_price is None:
        return

    if discount_price <= 0:
        raise InvalidDiscountPriceError()

    if discount_price >= price:
        raise InvalidDiscountPriceError()


def _validate_inventory(inventory):
    """
    Validates inventory value.
    """

    if inventory < 0:
        raise InvalidInventoryValueError()