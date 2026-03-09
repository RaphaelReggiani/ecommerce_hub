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
    MSG_PRODUCT_INVALID_TYPE,
    MSG_PRODUCT_INVALID_PRICE,
    MSG_PRODUCT_DISCOUNT_INVALID,
    MSG_PRODUCT_INVENTORY_INVALID,
    MSG_PRODUCT_OUT_OF_STOCK,
)


class ProductNotFoundError(ValidationError):
    """
    Raised when a product cannot be found.
    """
    def __init__(self):
        super().__init__(MSG_PRODUCT_NOT_FOUND)


class ProductInactiveError(ValidationError):
    """
    Raised when attempting to interact with an inactive product.
    """
    def __init__(self):
        super().__init__(MSG_PRODUCT_INACTIVE)


class ProductPermissionDeniedError(PermissionDenied):
    """
    Raised when a user does not have permission to perform an action on a product.
    """
    def __init__(self):
        super().__init__(MSG_PRODUCT_UPDATE_PERMISSION_DENIED)


class ProductCreationPermissionDeniedError(PermissionDenied):
    """
    Raised when a user tries to create a product without proper permissions.
    """
    def __init__(self):
        super().__init__(MSG_PRODUCT_CREATION_PERMISSION_DENIED)


class InvalidProductTypeError(ValidationError):
    """
    Raised when an invalid product type is provided.
    """
    def __init__(self):
        super().__init__(MSG_PRODUCT_INVALID_TYPE)


class InvalidProductPriceError(ValidationError):
    """
    Raised when an invalid price is provided.
    """
    def __init__(self):
        super().__init__(MSG_PRODUCT_INVALID_PRICE)


class InvalidDiscountPriceError(ValidationError):
    """
    Raised when the discount price is greater than or equal to the regular price.
    """
    def __init__(self):
        super().__init__(MSG_PRODUCT_DISCOUNT_INVALID)


class InvalidInventoryValueError(ValidationError):
    """
    Raised when an invalid inventory value is provided.
    """
    def __init__(self):
        super().__init__(MSG_PRODUCT_INVENTORY_INVALID)


class ProductOutOfStockError(ValidationError):
    """
    Raised when attempting to purchase a product with no inventory available.
    """
    def __init__(self):
        super().__init__(MSG_PRODUCT_OUT_OF_STOCK)


class ProductMinimumImagesError(ValidationError):
    """
    Raised when a product does not meet the minimum required number of images.
    """
    def __init__(self, min_images):
        message = MSG_PRODUCT_MIN_IMAGES_REQUIRED.format(min_images=min_images)
        super().__init__(message)