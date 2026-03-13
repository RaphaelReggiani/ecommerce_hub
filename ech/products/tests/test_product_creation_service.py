from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from ech.users.models import (
    CustomUser,
)

from ech.products.models import (
    Product, 
    ProductInventory,
)
from ech.products.services.product_creation_service import create_product

from ech.products.constants.roles_management import (
    ALLOWED_PRODUCTS_ROLES,
)
from ech.users.constants.constants import (
    CORPORATE_EMAIL_DOMAIN,
)

from ech.products.exceptions import (
    ProductCreationPermissionDeniedError,
    InvalidProductTypeError,
    InvalidProductPriceError,
    InvalidDiscountPriceError,
    InvalidInventoryValueError,
)


User = get_user_model()


class ProductCreationServiceTestCase(TestCase):

    def setUp(self):
        """
        Creates a valid operations user to run the tests.
        """

        self.allowed_role = list(ALLOWED_PRODUCTS_ROLES)[0]

        self.user = User.objects.create_user(
            email=f"ops{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            user_name="ops_user",
            role=self.allowed_role
        )

        self.valid_data = dict(
            user=self.user,
            name="Gaming Mouse",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="Logitech",
            description="High precision mouse",
            technical_information="16000 DPI sensor",
            price=Decimal("200.00"),
            discount_price=Decimal("150.00"),
            inventory=10,
        )

    def test_create_product_success(self):
        """
        Product and inventory should be created successfully.
        """

        product = create_product(**self.valid_data)

        self.assertIsInstance(product, Product)

        self.assertEqual(product.name, "Gaming Mouse")
        self.assertEqual(product.brand, "Logitech")

        inventory = ProductInventory.objects.get(product=product)

        self.assertEqual(inventory.quantity, 10)

    def test_create_product_without_discount(self):
        """
        Product should be created when discount_price is None.
        """

        data = self.valid_data.copy()
        data["discount_price"] = None

        product = create_product(**data)

        self.assertIsNone(product.discount_price)

    def test_create_product_default_inventory(self):
        """
        Product should be created with inventory = 0 if not provided.
        """

        data = self.valid_data.copy()
        data["inventory"] = 0

        product = create_product(**data)

        inventory = ProductInventory.objects.get(product=product)

        self.assertEqual(inventory.quantity, 0)

    def test_user_without_permission_cannot_create_product(self):
        """
        User without allowed role should not create products.
        """

        invalid_user = User.objects.create_user(
            email="user@gmail.com",
            password="StrongPassword123",
            user_name="normal_user",
            role=CustomUser.ROLE_CUSTOMER_USER
        )

        data = self.valid_data.copy()
        data["user"] = invalid_user

        with self.assertRaises(ProductCreationPermissionDeniedError):
            create_product(**data)

    def test_invalid_product_type(self):
        """
        Invalid product type should raise error.
        """

        data = self.valid_data.copy()
        data["product_type"] = "INVALID_TYPE"

        with self.assertRaises(InvalidProductTypeError):
            create_product(**data)

    def test_invalid_price_zero(self):
        """
        Price must be greater than zero.
        """

        data = self.valid_data.copy()
        data["price"] = Decimal("0")

        with self.assertRaises(InvalidProductPriceError):
            create_product(**data)

    def test_invalid_price_negative(self):
        """
        Negative price should raise error.
        """

        data = self.valid_data.copy()
        data["price"] = Decimal("-10")

        with self.assertRaises(InvalidProductPriceError):
            create_product(**data)

    def test_invalid_discount_negative(self):
        """
        Discount price must be positive.
        """

        data = self.valid_data.copy()
        data["discount_price"] = Decimal("-10")

        with self.assertRaises(InvalidDiscountPriceError):
            create_product(**data)

    def test_discount_greater_than_price(self):
        """
        Discount cannot be greater than or equal to price.
        """

        data = self.valid_data.copy()
        data["discount_price"] = Decimal("300")

        with self.assertRaises(InvalidDiscountPriceError):
            create_product(**data)

    def test_discount_equal_price(self):
        """
        Discount equal to price should raise error.
        """

        data = self.valid_data.copy()
        data["discount_price"] = Decimal("200")

        with self.assertRaises(InvalidDiscountPriceError):
            create_product(**data)

    def test_invalid_inventory_negative(self):
        """
        Inventory cannot be negative.
        """

        data = self.valid_data.copy()
        data["inventory"] = -5

        with self.assertRaises(InvalidInventoryValueError):
            create_product(**data)

    def test_product_not_created_when_validation_fails(self):
        """
        If validation fails, product must not be created (transaction safety).
        """

        data = self.valid_data.copy()
        data["price"] = Decimal("0")

        with self.assertRaises(InvalidProductPriceError):
            create_product(**data)

        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductInventory.objects.count(), 0)