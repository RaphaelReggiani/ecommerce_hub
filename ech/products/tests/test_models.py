from decimal import Decimal
from uuid import UUID, uuid4

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase

from ech.products.constants.inventory import DEFAULT_PRODUCT_INVENTORY
from ech.products.constants.storage import PRODUCT_IMAGES_UPLOAD_PATH
from ech.products.models import (
    Product,
    ProductEventLog,
    ProductImage,
    ProductInventory,
)
from ech.users.models import CustomUser


class ProductModelTestCase(TestCase):
    def setUp(self):
        self.staff_user = CustomUser.objects.create_user(
            email="staff@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Staff User",
        )

        self.product = Product.objects.create(
            name="Gaming Mouse",
            product_type=Product.MOUSE,
            brand="Logitech",
            sold_by=self.staff_user,
            description="High performance gaming mouse.",
            technical_information="16000 DPI sensor.",
            price=Decimal("299.90"),
            discount_price=Decimal("249.90"),
            is_active=True,
        )

    def test_product_is_created_successfully(self):
        """Ensure product is created successfully with valid data."""
        self.assertEqual(self.product.name, "Gaming Mouse")
        self.assertEqual(self.product.product_type, Product.MOUSE)
        self.assertEqual(self.product.brand, "Logitech")
        self.assertEqual(self.product.sold_by, self.staff_user)
        self.assertEqual(self.product.price, Decimal("299.90"))
        self.assertEqual(self.product.discount_price, Decimal("249.90"))
        self.assertTrue(self.product.is_active)

    def test_product_id_is_uuid(self):
        """Ensure product ID is generated as UUID."""
        self.assertIsInstance(self.product.id, UUID)

    def test_product_str_returns_name(self):
        """Ensure product string representation returns product name."""
        self.assertEqual(str(self.product), "Gaming Mouse")

    def test_product_has_discount_returns_true_when_discount_is_lower_than_price(self):
        """Ensure has_discount returns true when discount price is lower than price."""
        self.assertTrue(self.product.has_discount)

    def test_product_has_discount_returns_false_when_discount_is_none(self):
        """Ensure has_discount returns false when discount price is not set."""
        self.product.discount_price = None
        self.assertFalse(self.product.has_discount)

    def test_product_has_discount_returns_false_when_discount_is_equal_to_price(self):
        """Ensure has_discount returns false when discount price equals price."""
        self.product.discount_price = Decimal("299.90")
        self.assertFalse(self.product.has_discount)

    def test_product_has_discount_returns_false_when_discount_is_higher_than_price(self):
        """Ensure has_discount returns false when discount price is higher than price."""
        self.product.discount_price = Decimal("399.90")
        self.assertFalse(self.product.has_discount)

    def test_product_main_image_returns_none_when_product_has_no_images(self):
        """Ensure main_image returns none when product has no images."""
        self.assertIsNone(self.product.main_image)

    def test_product_main_image_returns_first_image_url_by_order(self):
        """Ensure main_image returns URL of the first ordered image."""
        image_2 = ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile(
                "mouse2.jpg",
                b"filecontent",
                content_type="image/jpeg",
            ),
            order=2,
        )
        image_1 = ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile(
                "mouse1.jpg",
                b"filecontent",
                content_type="image/jpeg",
            ),
            order=1,
        )

        self.assertIn(PRODUCT_IMAGES_UPLOAD_PATH, image_1.image.name)
        self.assertEqual(self.product.main_image, image_1.image.url)
        self.assertNotEqual(self.product.main_image, image_2.image.url)

    def test_product_inventory_property_returns_zero_when_inventory_record_does_not_exist(self):
        """Ensure inventory property returns zero when no inventory record exists."""
        self.assertEqual(self.product.inventory, 0)

    def test_product_inventory_property_returns_inventory_quantity(self):
        """Ensure inventory property returns quantity from inventory record."""
        ProductInventory.objects.create(
            product=self.product,
            quantity=15,
        )

        self.assertEqual(self.product.inventory, 15)

    def test_product_default_is_active_is_true(self):
        """Ensure product default active flag is true."""
        product = Product.objects.create(
            name="Mechanical Keyboard",
            product_type=Product.KEYBOARD,
            brand="Keychron",
            sold_by=self.staff_user,
            description="Mechanical keyboard.",
            technical_information="Wireless keyboard.",
            price=Decimal("499.90"),
        )

        self.assertTrue(product.is_active)

    def test_product_idempotency_fields_default_to_none(self):
        """Ensure idempotency fields default to None when not provided."""
        self.assertIsNone(self.product.idempotency_key)
        self.assertIsNone(self.product.idempotency_request_hash)

    def test_product_persists_idempotency_fields_when_provided(self):
        """Ensure idempotency key and request hash are persisted correctly."""
        idempotency_key = uuid4()
        request_hash = "a" * 64

        product = Product.objects.create(
            name="Idempotent Keyboard",
            product_type=Product.KEYBOARD,
            brand="Keychron",
            sold_by=self.staff_user,
            description="Keyboard with idempotency metadata.",
            technical_information="Wireless, RGB.",
            price=Decimal("499.90"),
            idempotency_key=idempotency_key,
            idempotency_request_hash=request_hash,
        )

        self.assertEqual(product.idempotency_key, idempotency_key)
        self.assertEqual(product.idempotency_request_hash, request_hash)

    def test_product_ordering_is_descending_by_created_at(self):
        """Ensure products are ordered by created_at descending."""
        older_product = Product.objects.create(
            name="Old Product",
            product_type=Product.PHONE,
            brand="Brand A",
            sold_by=self.staff_user,
            description="Old product description.",
            technical_information="Old product specs.",
            price=Decimal("100.00"),
        )
        newer_product = Product.objects.create(
            name="New Product",
            product_type=Product.HEADSET,
            brand="Brand B",
            sold_by=self.staff_user,
            description="New product description.",
            technical_information="New product specs.",
            price=Decimal("200.00"),
        )

        products = list(Product.objects.all())

        self.assertEqual(products[0], newer_product)
        self.assertIn(older_product, products)


class ProductInventoryModelTestCase(TestCase):
    def setUp(self):
        self.staff_user = CustomUser.objects.create_user(
            email="inventory@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Inventory User",
        )

        self.product = Product.objects.create(
            name="Studio Microphone",
            product_type=Product.MICROPHONE,
            brand="Shure",
            sold_by=self.staff_user,
            description="Professional studio microphone.",
            technical_information="Cardioid condenser microphone.",
            price=Decimal("899.90"),
        )

    def test_inventory_is_created_successfully(self):
        """Ensure inventory record is created successfully."""
        inventory = ProductInventory.objects.create(
            product=self.product,
            quantity=20,
        )

        self.assertEqual(inventory.product, self.product)
        self.assertEqual(inventory.quantity, 20)

    def test_inventory_default_quantity_is_zero(self):
        """Ensure inventory default quantity is zero."""
        inventory = ProductInventory.objects.create(
            product=self.product,
        )

        self.assertEqual(inventory.quantity, DEFAULT_PRODUCT_INVENTORY)

    def test_inventory_str_returns_expected_value(self):
        """Ensure inventory string representation includes product ID and quantity."""
        inventory = ProductInventory.objects.create(
            product=self.product,
            quantity=7,
        )

        self.assertEqual(
            str(inventory),
            f"{self.product.id} inventory: 7",
        )

    def test_inventory_relation_is_one_to_one(self):
        """Ensure only one inventory record can exist per product."""
        ProductInventory.objects.create(
            product=self.product,
            quantity=10,
        )

        with self.assertRaises(IntegrityError):
            ProductInventory.objects.create(
                product=self.product,
                quantity=20,
            )


class ProductImageModelTestCase(TestCase):
    def setUp(self):
        self.staff_user = CustomUser.objects.create_user(
            email="images@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Image User",
        )

        self.product = Product.objects.create(
            name="Wireless Earphone",
            product_type=Product.EARPHONE,
            brand="Sony",
            sold_by=self.staff_user,
            description="Wireless earphone description.",
            technical_information="Bluetooth 5.3.",
            price=Decimal("399.90"),
        )

    def test_product_image_is_created_successfully(self):
        """Ensure product image is created successfully."""
        image = ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile(
                "earphone.jpg",
                b"filecontent",
                content_type="image/jpeg",
            ),
            order=1,
        )

        self.assertEqual(image.product, self.product)
        self.assertEqual(image.order, 1)
        self.assertIn(PRODUCT_IMAGES_UPLOAD_PATH, image.image.name)

    def test_product_image_str_returns_expected_value(self):
        """Ensure product image string representation is correct."""
        image = ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile(
                "earphone.jpg",
                b"filecontent",
                content_type="image/jpeg",
            ),
            order=1,
        )

        self.assertEqual(str(image), f"{self.product.name} - Image 1")

    def test_product_image_order_must_be_greater_than_or_equal_to_one(self):
        """Ensure product image order must be at least one."""
        image = ProductImage(
            product=self.product,
            image=SimpleUploadedFile(
                "invalid.jpg",
                b"filecontent",
                content_type="image/jpeg",
            ),
            order=0,
        )

        with self.assertRaises(ValidationError):
            image.full_clean()

    def test_product_image_order_must_be_unique_per_product(self):
        """Ensure image order is unique for the same product."""
        ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile(
                "img1.jpg",
                b"filecontent",
                content_type="image/jpeg",
            ),
            order=1,
        )

        duplicate_image = ProductImage(
            product=self.product,
            image=SimpleUploadedFile(
                "img2.jpg",
                b"filecontent",
                content_type="image/jpeg",
            ),
            order=1,
        )

        with self.assertRaises(ValidationError):
            duplicate_image.full_clean()

    def test_product_image_ordering_is_ascending_by_order(self):
        """Ensure product images are ordered by display order ascending."""
        image_2 = ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile(
                "img2.jpg",
                b"filecontent",
                content_type="image/jpeg",
            ),
            order=2,
        )
        image_1 = ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile(
                "img1.jpg",
                b"filecontent",
                content_type="image/jpeg",
            ),
            order=1,
        )

        images = list(self.product.images.all())

        self.assertEqual(images[0], image_1)
        self.assertEqual(images[1], image_2)

    def test_product_image_allows_supported_file_extensions(self):
        """Ensure product image accepts supported file extensions."""
        for filename in ["image.jpg", "image.jpeg", "image.png", "image.webp"]:
            image = ProductImage(
                product=self.product,
                image=SimpleUploadedFile(
                    filename,
                    b"filecontent",
                    content_type="image/jpeg",
                ),
                order=1,
            )
            image.full_clean()

    def test_product_image_rejects_unsupported_file_extension(self):
        """Ensure product image rejects unsupported file extensions."""
        image = ProductImage(
            product=self.product,
            image=SimpleUploadedFile(
                "image.gif",
                b"filecontent",
                content_type="image/gif",
            ),
            order=1,
        )

        with self.assertRaises(ValidationError):
            image.full_clean()


class ProductEventLogModelTestCase(TestCase):
    def setUp(self):
        self.staff_user = CustomUser.objects.create_user(
            email="events@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Event User",
        )

        self.product = Product.objects.create(
            name="Office Headset",
            product_type=Product.HEADSET,
            brand="JBL",
            sold_by=self.staff_user,
            description="Office headset description.",
            technical_information="Noise cancelling headset.",
            price=Decimal("599.90"),
        )

    def test_product_event_log_is_created_successfully(self):
        """Ensure product event log is created successfully."""
        event = ProductEventLog.objects.create(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_CREATED,
            performed_by=self.staff_user,
            metadata={"source": "test"},
        )

        self.assertEqual(event.product, self.product)
        self.assertEqual(event.event_type, ProductEventLog.EVENT_PRODUCT_CREATED)
        self.assertEqual(event.performed_by, self.staff_user)
        self.assertEqual(event.metadata, {"source": "test"})

    def test_product_event_log_id_is_uuid(self):
        """Ensure product event log ID is generated as UUID."""
        event = ProductEventLog.objects.create(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_UPDATED,
            performed_by=self.staff_user,
        )

        self.assertIsInstance(event.id, UUID)

    def test_product_event_log_str_returns_expected_value(self):
        """Ensure product event log string representation is correct."""
        event = ProductEventLog.objects.create(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_UPDATED,
            performed_by=self.staff_user,
        )

        self.assertEqual(
            str(event),
            f"{self.product.id} - {ProductEventLog.EVENT_PRODUCT_UPDATED}",
        )

    def test_product_event_log_allows_null_performed_by(self):
        """Ensure product event log allows null performer."""
        event = ProductEventLog.objects.create(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_DELETED,
            performed_by=None,
        )

        self.assertIsNone(event.performed_by)

    def test_product_event_log_allows_null_metadata(self):
        """Ensure product event log allows null metadata."""
        event = ProductEventLog.objects.create(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_IMAGE_UPLOADED,
            performed_by=self.staff_user,
            metadata=None,
        )

        self.assertIsNone(event.metadata)

    def test_product_event_log_ordering_is_descending_by_created_at(self):
        """Ensure product event logs are ordered by created_at descending."""
        older_event = ProductEventLog.objects.create(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_CREATED,
            performed_by=self.staff_user,
        )
        newer_event = ProductEventLog.objects.create(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_UPDATED,
            performed_by=self.staff_user,
        )

        events = list(ProductEventLog.objects.all())

        self.assertEqual(events[0], newer_event)
        self.assertIn(older_event, events)