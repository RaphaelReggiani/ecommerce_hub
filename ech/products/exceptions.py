from django.core.exceptions import (
    ValidationError,
    PermissionDenied,
)

from ech.products.constants.messages import (
    MSG_PRODUCT_NOT_FOUND,
    MSG_PRODUCT_CREATION_PERMISSION_DENIED,
    MSG_PRODUCT_UPDATE_PERMISSION_DENIED,
    MSG_PRODUCT_INACTIVE,
    MSG_PRODUCT_MIN_IMAGES_REQUIRED,
    MSG_PRODUCT_MAX_IMAGES_REQUIRED,
    MSG_PRODUCT_INVALID_TYPE,
    MSG_PRODUCT_INVALID_PRICE,
    MSG_PRODUCT_DISCOUNT_INVALID,
    MSG_PRODUCT_INVENTORY_INVALID,
    MSG_PRODUCT_OUT_OF_STOCK,
    MSG_IDEMPOTENCY_CONFLICT,
)


class ProductDomainError(Exception):
    """
    Base exception for all product domain-related errors.
    """

    default_message = "Product domain error."

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class IdempotencyConflictError(ProductDomainError):
    """
    Raised when the same idempotency key is reused
    with a different request payload.
    """

    default_message = MSG_IDEMPOTENCY_CONFLICT


class ProductNotFoundError(ProductDomainError):
    """
    Raised when a product cannot be found.
    """

    default_message = MSG_PRODUCT_NOT_FOUND


class ProductInactiveError(ProductDomainError):
    """
    Raised when attempting to interact with an inactive product.
    """

    default_message = MSG_PRODUCT_INACTIVE


class ProductPermissionDeniedError(PermissionDenied):
    """
    Raised when a user does not have permission
    to perform an action on a product.
    """

    def __init__(self):
        super().__init__(MSG_PRODUCT_UPDATE_PERMISSION_DENIED)


class ProductCreationPermissionDeniedError(PermissionDenied):
    """
    Raised when a user tries to create a product
    without proper permissions.
    """

    def __init__(self):
        super().__init__(MSG_PRODUCT_CREATION_PERMISSION_DENIED)


class InvalidProductTypeError(ProductDomainError):
    """
    Raised when an invalid product type is provided.
    """

    default_message = MSG_PRODUCT_INVALID_TYPE


class InvalidProductPriceError(ProductDomainError):
    """
    Raised when an invalid price is provided.
    """

    default_message = MSG_PRODUCT_INVALID_PRICE


class InvalidDiscountPriceError(ProductDomainError):
    """
    Raised when the discount price is greater than or equal to the regular price.
    """

    default_message = MSG_PRODUCT_DISCOUNT_INVALID


class InvalidInventoryValueError(ProductDomainError):
    """
    Raised when an invalid inventory value is provided.
    """

    default_message = MSG_PRODUCT_INVENTORY_INVALID


class ProductOutOfStockError(ProductDomainError):
    """
    Raised when attempting to purchase a product with no inventory available.
    """

    default_message = MSG_PRODUCT_OUT_OF_STOCK


class ProductMinimumImagesError(ProductDomainError):
    """
    Raised when a product does not meet the minimum required number of images.
    """

    def __init__(self, min_images):
        message = MSG_PRODUCT_MIN_IMAGES_REQUIRED.format(min_images=min_images)
        super().__init__(message)


class ProductMaximumImagesError(ProductDomainError):
    """
    Raised when the maximum number of product images is exceeded.
    """

    def __init__(self, max_images):
        self.max_images = max_images
        message = MSG_PRODUCT_MAX_IMAGES_REQUIRED.format(max_images=max_images)
        super().__init__(message)