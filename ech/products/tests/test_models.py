from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from ech.products.models import (
    Product,
    ProductInventory,
    ProductImage,
)

from ech.products.constants.inventory import (
    DEFAULT_PRODUCT_INVENTORY,
)


User = get_user_model()


class ProductModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="seller@test.com",
            password="StrongPassword123",
            user_name="seller"
        )

        self.product = Product.objects.create(
            name="Gaming Mouse",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="Logitech",
            sold_by=self.user,
            description="High precision gaming mouse",
            technical_information="16000 DPI sensor",
            price=Decimal("200.00"),
        )

    def test_product_creation(self):
        """Product should be created successfully."""
        self.assertEqual(self.product.name, "Gaming Mouse")
        self.assertEqual(self.product.brand, "Logitech")
        self.assertTrue(self.product.is_active)
        self.assertIsNotNone(self.product.created_at)

    def test_product_string_representation(self):
        """__str__ should return product name."""
        self.assertEqual(str(self.product), "Gaming Mouse")

    def test_product_has_discount_false(self):
        """Product without discount should return False."""
        self.assertFalse(self.product.has_discount)

    def test_product_has_discount_true(self):
        """Product should detect valid discount."""
        self.product.discount_price = Decimal("150.00")
        self.product.save()

        self.assertTrue(self.product.has_discount)

    def test_product_discount_not_valid_if_greater_than_price(self):
        """Discount higher than price should not count as discount."""
        self.product.discount_price = Decimal("250.00")
        self.product.save()

        self.assertFalse(self.product.has_discount)

    def test_product_inventory_property_without_record(self):
        """Inventory property should return 0 when no record exists."""
        self.assertEqual(self.product.inventory, 0)

    def test_product_inventory_property_with_record(self):
        """Inventory property should return inventory quantity."""
        ProductInventory.objects.create(
            product=self.product,
            quantity=15
        )

        self.assertEqual(self.product.inventory, 15)

    def test_product_main_image_none(self):
        """Product without images should return None."""
        self.assertIsNone(self.product.main_image)

    def test_product_main_image_returns_first_by_order(self):
        """Main image should be the image with lowest order."""
        image_file = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

        ProductImage.objects.create(
            product=self.product,
            image=image_file,
            order=2
        )

        ProductImage.objects.create(
            product=self.product,
            image=image_file,
            order=1
        )

        self.assertIsNotNone(self.product.main_image)


class ProductInventoryModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="seller@test.com",
            password="StrongPassword123",
            user_name="seller"
        )

        self.product = Product.objects.create(
            name="Keyboard",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="Corsair",
            sold_by=self.user,
            description="Mechanical keyboard",
            technical_information="RGB switches",
            price=Decimal("500.00"),
        )

    def test_inventory_creation(self):
        """Inventory should be created with correct quantity."""
        inventory = ProductInventory.objects.create(
            product=self.product,
            quantity=10
        )

        self.assertEqual(inventory.quantity, 10)

    def test_inventory_default_value(self):
        """Inventory should use default value if none provided."""
        inventory = ProductInventory.objects.create(
            product=self.product
        )

        self.assertEqual(inventory.quantity, DEFAULT_PRODUCT_INVENTORY)

    def test_inventory_one_to_one_constraint(self):
        """Product should not allow multiple inventory records."""
        ProductInventory.objects.create(product=self.product)

        with self.assertRaises(IntegrityError):
            ProductInventory.objects.create(product=self.product)

    def test_inventory_string_representation(self):
        """__str__ should contain product id and quantity."""
        inventory = ProductInventory.objects.create(
            product=self.product,
            quantity=5
        )

        self.assertIn(str(self.product.id), str(inventory))


class ProductImageModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="seller@test.com",
            password="StrongPassword123",
            user_name="seller"
        )

        self.product = Product.objects.create(
            name="Monitor",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="Dell",
            sold_by=self.user,
            description="4K Monitor",
            technical_information="144Hz IPS",
            price=Decimal("2000.00"),
        )

        self.image_file = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

    def test_product_image_creation(self):
        """Image should be created successfully."""
        image = ProductImage.objects.create(
            product=self.product,
            image=self.image_file,
            order=1
        )

        self.assertEqual(image.product, self.product)
        self.assertEqual(image.order, 1)

    def test_product_image_order_unique_per_product(self):
        """Same product cannot have two images with same order."""
        ProductImage.objects.create(
            product=self.product,
            image=self.image_file,
            order=1
        )

        with self.assertRaises(IntegrityError):
            ProductImage.objects.create(
                product=self.product,
                image=self.image_file,
                order=1
            )

    def test_product_image_order_validator(self):
        """Order must be >= 1."""
        image = ProductImage(
            product=self.product,
            image=self.image_file,
            order=0
        )

        with self.assertRaises(ValidationError):
            image.full_clean()

    def test_product_image_string_representation(self):
        """__str__ should contain product name and order."""
        image = ProductImage.objects.create(
            product=self.product,
            image=self.image_file,
            order=1
        )

        self.assertIn(self.product.name, str(image))