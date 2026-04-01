import hashlib
import json
import uuid

from django.db import IntegrityError, transaction

from ech.products.constants.roles_management import (
    ALLOWED_PRODUCTS_ROLES,
)
from ech.products.domain_events.dispatcher import EventDispatcher
from ech.products.domain_events.events import ProductCreatedEvent
from ech.products.exceptions import (
    IdempotencyConflictError,
    InvalidDiscountPriceError,
    InvalidInventoryValueError,
    InvalidProductPriceError,
    InvalidProductTypeError,
    ProductCreationPermissionDeniedError,
)
from ech.products.models import (
    Product,
    ProductInventory,
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
    idempotency_key=None,
):
    """
    Creates a new product.

    Images are uploaded in a second step via:
    POST /products/{id}/images/

    Only Operations Staff, Admin and SuperAdmin can create products.

    Supports idempotent creation when an Idempotency-Key is provided.
    """

    _validate_user_permission(user)
    _validate_product_type(product_type)
    _validate_price(price)
    _validate_discount(price, discount_price)
    _validate_inventory(inventory)

    normalized_idempotency_key = _normalize_idempotency_key(idempotency_key)

    request_hash = _build_product_creation_request_hash(
        user=user,
        name=name,
        product_type=product_type,
        brand=brand,
        description=description,
        technical_information=technical_information,
        price=price,
        discount_price=discount_price,
        inventory=inventory,
    )

    existing_product = _get_product_by_idempotency_key(normalized_idempotency_key)
    if existing_product is not None:
        _validate_idempotent_replay(
            product=existing_product,
            request_hash=request_hash,
        )
        return existing_product

    try:
        product = Product.objects.create(
            name=name,
            product_type=product_type,
            brand=brand,
            sold_by=user,
            description=description,
            technical_information=technical_information,
            price=price,
            discount_price=discount_price,
            idempotency_key=normalized_idempotency_key,
            idempotency_request_hash=request_hash,
        )

        ProductInventory.objects.create(
            product=product,
            quantity=inventory,
        )

    except IntegrityError:
        if normalized_idempotency_key is not None:
            existing_product = _get_product_by_idempotency_key(
                normalized_idempotency_key
            )
            if existing_product is not None:
                _validate_idempotent_replay(
                    product=existing_product,
                    request_hash=request_hash,
                )
                return existing_product

        raise

    EventDispatcher.dispatch(
        ProductCreatedEvent(
            product=product,
            performed_by=user,
        )
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


def _normalize_idempotency_key(idempotency_key):
    """
    Normalizes the incoming idempotency key into a UUID object.
    Returns None when the key is not provided.
    """

    if not idempotency_key:
        return None

    if isinstance(idempotency_key, uuid.UUID):
        return idempotency_key

    return uuid.UUID(str(idempotency_key))


def _get_product_by_idempotency_key(idempotency_key):
    """
    Retrieves an existing product by idempotency key.
    """

    if idempotency_key is None:
        return None

    return Product.objects.filter(idempotency_key=idempotency_key).first()


def _build_product_creation_request_hash(
    *,
    user,
    name,
    product_type,
    brand,
    description,
    technical_information,
    price,
    discount_price,
    inventory,
):
    """
    Builds a deterministic hash for the product creation payload.
    """

    normalized_payload = {
        "user_id": str(user.pk),
        "name": name,
        "product_type": product_type,
        "brand": brand,
        "description": description,
        "technical_information": technical_information,
        "price": str(price),
        "discount_price": str(discount_price) if discount_price is not None else None,
        "inventory": inventory,
    }

    payload_json = json.dumps(
        normalized_payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()


def _validate_idempotent_replay(*, product, request_hash):
    """
    Validates whether a repeated request with the same idempotency key
    matches the original payload.
    """

    stored_hash = getattr(product, "idempotency_request_hash", None)

    if stored_hash and stored_hash != request_hash:
        raise IdempotencyConflictError()