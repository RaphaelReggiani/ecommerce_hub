from django.core.exceptions import PermissionDenied, ValidationError
from django.test import SimpleTestCase

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
)
from ech.products.exceptions import (
    ProductNotFoundError,
    ProductInactiveError,
    ProductPermissionDeniedError,
    ProductCreationPermissionDeniedError,
    InvalidProductTypeError,
    InvalidProductPriceError,
    InvalidDiscountPriceError,
    InvalidInventoryValueError,
    ProductOutOfStockError,
    ProductMinimumImagesError,
    ProductMaximumImagesError,
)


class ProductNotFoundErrorTestCase(SimpleTestCase):
    def test_inherits_from_validation_error(self):
        """Ensure ProductNotFoundError inherits from ValidationError."""
        self.assertIsInstance(ProductNotFoundError(), ValidationError)

    def test_uses_expected_message(self):
        """Ensure ProductNotFoundError uses the correct default message."""
        error = ProductNotFoundError()
        self.assertEqual(error.message, MSG_PRODUCT_NOT_FOUND)


class ProductInactiveErrorTestCase(SimpleTestCase):
    def test_inherits_from_validation_error(self):
        """Ensure ProductInactiveError inherits from ValidationError."""
        self.assertIsInstance(ProductInactiveError(), ValidationError)

    def test_uses_expected_message(self):
        """Ensure ProductInactiveError uses the correct default message."""
        error = ProductInactiveError()
        self.assertEqual(error.message, MSG_PRODUCT_INACTIVE)


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
    def test_inherits_from_validation_error(self):
        """Ensure InvalidProductTypeError inherits from ValidationError."""
        self.assertIsInstance(InvalidProductTypeError(), ValidationError)

    def test_uses_expected_message(self):
        """Ensure InvalidProductTypeError uses the correct default message."""
        error = InvalidProductTypeError()
        self.assertEqual(error.message, MSG_PRODUCT_INVALID_TYPE)


class InvalidProductPriceErrorTestCase(SimpleTestCase):
    def test_inherits_from_validation_error(self):
        """Ensure InvalidProductPriceError inherits from ValidationError."""
        self.assertIsInstance(InvalidProductPriceError(), ValidationError)

    def test_uses_expected_message(self):
        """Ensure InvalidProductPriceError uses the correct default message."""
        error = InvalidProductPriceError()
        self.assertEqual(error.message, MSG_PRODUCT_INVALID_PRICE)


class InvalidDiscountPriceErrorTestCase(SimpleTestCase):
    def test_inherits_from_validation_error(self):
        """Ensure InvalidDiscountPriceError inherits from ValidationError."""
        self.assertIsInstance(InvalidDiscountPriceError(), ValidationError)

    def test_uses_expected_message(self):
        """Ensure InvalidDiscountPriceError uses the correct default message."""
        error = InvalidDiscountPriceError()
        self.assertEqual(error.message, MSG_PRODUCT_DISCOUNT_INVALID)


class InvalidInventoryValueErrorTestCase(SimpleTestCase):
    def test_inherits_from_validation_error(self):
        """Ensure InvalidInventoryValueError inherits from ValidationError."""
        self.assertIsInstance(InvalidInventoryValueError(), ValidationError)

    def test_uses_expected_message(self):
        """Ensure InvalidInventoryValueError uses the correct default message."""
        error = InvalidInventoryValueError()
        self.assertEqual(error.message, MSG_PRODUCT_INVENTORY_INVALID)


class ProductOutOfStockErrorTestCase(SimpleTestCase):
    def test_inherits_from_validation_error(self):
        """Ensure ProductOutOfStockError inherits from ValidationError."""
        self.assertIsInstance(ProductOutOfStockError(), ValidationError)

    def test_uses_expected_message(self):
        """Ensure ProductOutOfStockError uses the correct default message."""
        error = ProductOutOfStockError()
        self.assertEqual(error.message, MSG_PRODUCT_OUT_OF_STOCK)


class ProductMinimumImagesErrorTestCase(SimpleTestCase):
    def test_inherits_from_validation_error(self):
        """Ensure ProductMinimumImagesError inherits from ValidationError."""
        self.assertIsInstance(ProductMinimumImagesError(min_images=1), ValidationError)

    def test_formats_message_with_min_images_value(self):
        """Ensure ProductMinimumImagesError formats the minimum images message."""
        error = ProductMinimumImagesError(min_images=2)
        self.assertEqual(
            error.message,
            MSG_PRODUCT_MIN_IMAGES_REQUIRED.format(min_images=2),
        )


class ProductMaximumImagesErrorTestCase(SimpleTestCase):
    def test_inherits_from_exception(self):
        """Ensure ProductMaximumImagesError inherits from Exception."""
        self.assertIsInstance(ProductMaximumImagesError(max_images=5), Exception)

    def test_stores_max_images_value(self):
        """Ensure ProductMaximumImagesError stores the max_images value."""
        error = ProductMaximumImagesError(max_images=5)
        self.assertEqual(error.max_images, 5)

    def test_formats_message_with_max_images_value(self):
        """Ensure ProductMaximumImagesError formats the maximum images message."""
        error = ProductMaximumImagesError(max_images=5)
        self.assertEqual(
            str(error),
            MSG_PRODUCT_MAX_IMAGES_REQUIRED.format(max_images=5),
        )