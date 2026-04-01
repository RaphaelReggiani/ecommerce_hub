from django.core.exceptions import PermissionDenied
from django.test import SimpleTestCase

from ech.products.constants.messages import (
    MSG_IDEMPOTENCY_CONFLICT,
    MSG_PRODUCT_CREATION_PERMISSION_DENIED,
    MSG_PRODUCT_DISCOUNT_INVALID,
    MSG_PRODUCT_INACTIVE,
    MSG_PRODUCT_INVENTORY_INVALID,
    MSG_PRODUCT_INVALID_PRICE,
    MSG_PRODUCT_INVALID_TYPE,
    MSG_PRODUCT_MAX_IMAGES_REQUIRED,
    MSG_PRODUCT_MIN_IMAGES_REQUIRED,
    MSG_PRODUCT_NOT_FOUND,
    MSG_PRODUCT_OUT_OF_STOCK,
    MSG_PRODUCT_UPDATE_PERMISSION_DENIED,
)
from ech.products.exceptions import (
    IdempotencyConflictError,
    InvalidDiscountPriceError,
    InvalidInventoryValueError,
    InvalidProductPriceError,
    InvalidProductTypeError,
    ProductCreationPermissionDeniedError,
    ProductDomainError,
    ProductInactiveError,
    ProductMaximumImagesError,
    ProductMinimumImagesError,
    ProductNotFoundError,
    ProductOutOfStockError,
    ProductPermissionDeniedError,
)


class ProductDomainErrorTestCase(SimpleTestCase):
    def test_uses_default_message_when_none_is_provided(self):
        """Ensure ProductDomainError uses the default message."""
        error = ProductDomainError()
        self.assertEqual(error.message, "Product domain error.")
        self.assertEqual(str(error), "Product domain error.")

    def test_uses_custom_message_when_provided(self):
        """Ensure ProductDomainError accepts a custom message."""
        error = ProductDomainError("Custom product error.")
        self.assertEqual(error.message, "Custom product error.")
        self.assertEqual(str(error), "Custom product error.")


class IdempotencyConflictErrorTestCase(SimpleTestCase):
    def test_inherits_from_product_domain_error(self):
        """Ensure IdempotencyConflictError inherits from ProductDomainError."""
        self.assertIsInstance(IdempotencyConflictError(), ProductDomainError)

    def test_uses_expected_message(self):
        """Ensure IdempotencyConflictError uses the correct default message."""
        error = IdempotencyConflictError()
        self.assertEqual(error.message, MSG_IDEMPOTENCY_CONFLICT)
        self.assertEqual(str(error), MSG_IDEMPOTENCY_CONFLICT)


class ProductNotFoundErrorTestCase(SimpleTestCase):
    def test_inherits_from_product_domain_error(self):
        """Ensure ProductNotFoundError inherits from ProductDomainError."""
        self.assertIsInstance(ProductNotFoundError(), ProductDomainError)

    def test_uses_expected_message(self):
        """Ensure ProductNotFoundError uses the correct default message."""
        error = ProductNotFoundError()
        self.assertEqual(error.message, MSG_PRODUCT_NOT_FOUND)
        self.assertEqual(str(error), MSG_PRODUCT_NOT_FOUND)


class ProductInactiveErrorTestCase(SimpleTestCase):
    def test_inherits_from_product_domain_error(self):
        """Ensure ProductInactiveError inherits from ProductDomainError."""
        self.assertIsInstance(ProductInactiveError(), ProductDomainError)

    def test_uses_expected_message(self):
        """Ensure ProductInactiveError uses the correct default message."""
        error = ProductInactiveError()
        self.assertEqual(error.message, MSG_PRODUCT_INACTIVE)
        self.assertEqual(str(error), MSG_PRODUCT_INACTIVE)


class ProductPermissionDeniedErrorTestCase(SimpleTestCase):
    def test_inherits_from_permission_denied(self):
        """Ensure ProductPermissionDeniedError inherits from PermissionDenied."""
        self.assertIsInstance(ProductPermissionDeniedError(), PermissionDenied)

    def test_uses_expected_message(self):
        """Ensure ProductPermissionDeniedError uses the correct default message."""
        error = ProductPermissionDeniedError()
        self.assertEqual(str(error), MSG_PRODUCT_UPDATE_PERMISSION_DENIED)


class ProductCreationPermissionDeniedErrorTestCase(SimpleTestCase):
    def test_inherits_from_permission_denied(self):
        """Ensure ProductCreationPermissionDeniedError inherits from PermissionDenied."""
        self.assertIsInstance(ProductCreationPermissionDeniedError(), PermissionDenied)

    def test_uses_expected_message(self):
        """Ensure ProductCreationPermissionDeniedError uses the correct default message."""
        error = ProductCreationPermissionDeniedError()
        self.assertEqual(str(error), MSG_PRODUCT_CREATION_PERMISSION_DENIED)


class InvalidProductTypeErrorTestCase(SimpleTestCase):
    def test_inherits_from_product_domain_error(self):
        """Ensure InvalidProductTypeError inherits from ProductDomainError."""
        self.assertIsInstance(InvalidProductTypeError(), ProductDomainError)

    def test_uses_expected_message(self):
        """Ensure InvalidProductTypeError uses the correct default message."""
        error = InvalidProductTypeError()
        self.assertEqual(error.message, MSG_PRODUCT_INVALID_TYPE)
        self.assertEqual(str(error), MSG_PRODUCT_INVALID_TYPE)


class InvalidProductPriceErrorTestCase(SimpleTestCase):
    def test_inherits_from_product_domain_error(self):
        """Ensure InvalidProductPriceError inherits from ProductDomainError."""
        self.assertIsInstance(InvalidProductPriceError(), ProductDomainError)

    def test_uses_expected_message(self):
        """Ensure InvalidProductPriceError uses the correct default message."""
        error = InvalidProductPriceError()
        self.assertEqual(error.message, MSG_PRODUCT_INVALID_PRICE)
        self.assertEqual(str(error), MSG_PRODUCT_INVALID_PRICE)


class InvalidDiscountPriceErrorTestCase(SimpleTestCase):
    def test_inherits_from_product_domain_error(self):
        """Ensure InvalidDiscountPriceError inherits from ProductDomainError."""
        self.assertIsInstance(InvalidDiscountPriceError(), ProductDomainError)

    def test_uses_expected_message(self):
        """Ensure InvalidDiscountPriceError uses the correct default message."""
        error = InvalidDiscountPriceError()
        self.assertEqual(error.message, MSG_PRODUCT_DISCOUNT_INVALID)
        self.assertEqual(str(error), MSG_PRODUCT_DISCOUNT_INVALID)


class InvalidInventoryValueErrorTestCase(SimpleTestCase):
    def test_inherits_from_product_domain_error(self):
        """Ensure InvalidInventoryValueError inherits from ProductDomainError."""
        self.assertIsInstance(InvalidInventoryValueError(), ProductDomainError)

    def test_uses_expected_message(self):
        """Ensure InvalidInventoryValueError uses the correct default message."""
        error = InvalidInventoryValueError()
        self.assertEqual(error.message, MSG_PRODUCT_INVENTORY_INVALID)
        self.assertEqual(str(error), MSG_PRODUCT_INVENTORY_INVALID)


class ProductOutOfStockErrorTestCase(SimpleTestCase):
    def test_inherits_from_product_domain_error(self):
        """Ensure ProductOutOfStockError inherits from ProductDomainError."""
        self.assertIsInstance(ProductOutOfStockError(), ProductDomainError)

    def test_uses_expected_message(self):
        """Ensure ProductOutOfStockError uses the correct default message."""
        error = ProductOutOfStockError()
        self.assertEqual(error.message, MSG_PRODUCT_OUT_OF_STOCK)
        self.assertEqual(str(error), MSG_PRODUCT_OUT_OF_STOCK)


class ProductMinimumImagesErrorTestCase(SimpleTestCase):
    def test_inherits_from_product_domain_error(self):
        """Ensure ProductMinimumImagesError inherits from ProductDomainError."""
        self.assertIsInstance(ProductMinimumImagesError(min_images=1), ProductDomainError)

    def test_formats_message_with_min_images_value(self):
        """Ensure ProductMinimumImagesError formats the minimum images message."""
        error = ProductMinimumImagesError(min_images=2)
        self.assertEqual(
            error.message,
            MSG_PRODUCT_MIN_IMAGES_REQUIRED.format(min_images=2),
        )
        self.assertEqual(
            str(error),
            MSG_PRODUCT_MIN_IMAGES_REQUIRED.format(min_images=2),
        )


class ProductMaximumImagesErrorTestCase(SimpleTestCase):
    def test_inherits_from_product_domain_error(self):
        """Ensure ProductMaximumImagesError inherits from ProductDomainError."""
        self.assertIsInstance(ProductMaximumImagesError(max_images=5), ProductDomainError)

    def test_formats_message_with_max_images_value(self):
        """Ensure ProductMaximumImagesError formats the maximum images message."""
        error = ProductMaximumImagesError(max_images=5)
        self.assertEqual(
            error.message,
            MSG_PRODUCT_MAX_IMAGES_REQUIRED.format(max_images=5),
        )
        self.assertEqual(
            str(error),
            MSG_PRODUCT_MAX_IMAGES_REQUIRED.format(max_images=5),
        )