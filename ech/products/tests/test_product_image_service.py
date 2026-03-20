from decimal import Decimal
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ech.users.models import CustomUser
from ech.products.constants.rules import ProductImageRules
from ech.products.exceptions import (
    ProductMaximumImagesError,
    ProductMinimumImagesError,
    ProductNotFoundError,
)
from ech.products.models import Product, ProductImage
from ech.products.services.product_image_service import (
    add_product_image,
    validate_product_minimum_images,
)


class ProductImageServiceTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="staff@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Staff User",
        )

        self.product = Product.objects.create(
            name="Gaming Headset",
            product_type=Product.HEADSET,
            brand="HyperX",
            sold_by=self.user,
            description="Gaming headset description",
            technical_information="7.1 surround sound",
            price=Decimal("399.90"),
            is_active=True,
        )

    def _make_image(self, name):
        """Create a valid uploaded image file for tests."""
        return SimpleUploadedFile(
            name,
            b"filecontent",
            content_type="image/jpeg",
        )

    def test_add_product_image_adds_single_image_successfully(self):
        """Ensure add_product_image adds a single image successfully."""
        created_images = add_product_image(
            product_id=self.product.id,
            images=[self._make_image("image1.jpg")],
        )

        self.assertEqual(len(created_images), 1)
        self.assertEqual(created_images[0].product, self.product)
        self.assertEqual(created_images[0].order, 1)
        self.assertEqual(ProductImage.objects.filter(product=self.product).count(), 1)

    def test_add_product_image_adds_multiple_images_successfully(self):
        """Ensure add_product_image adds multiple images successfully."""
        created_images = add_product_image(
            product_id=self.product.id,
            images=[
                self._make_image("image1.jpg"),
                self._make_image("image2.jpg"),
                self._make_image("image3.jpg"),
            ],
        )

        self.assertEqual(len(created_images), 3)
        self.assertEqual(created_images[0].order, 1)
        self.assertEqual(created_images[1].order, 2)
        self.assertEqual(created_images[2].order, 3)
        self.assertEqual(ProductImage.objects.filter(product=self.product).count(), 3)

    def test_add_product_image_returns_empty_list_when_images_is_empty(self):
        """Ensure add_product_image returns an empty list when no images are provided."""
        created_images = add_product_image(
            product_id=self.product.id,
            images=[],
        )

        self.assertEqual(created_images, [])
        self.assertEqual(ProductImage.objects.filter(product=self.product).count(), 0)

    def test_add_product_image_raises_product_not_found_error_when_product_does_not_exist(self):
        """Ensure add_product_image raises ProductNotFoundError for missing product."""
        with self.assertRaises(ProductNotFoundError):
            add_product_image(
                product_id=uuid.uuid4(),
                images=[self._make_image("image1.jpg")],
            )

    def test_add_product_image_raises_maximum_images_error_when_limit_is_exceeded(self):
        """Ensure add_product_image raises ProductMaximumImagesError when max limit is exceeded."""
        for index in range(ProductImageRules.MAX_IMAGES_ALLOWED):
            ProductImage.objects.create(
                product=self.product,
                image=self._make_image(f"existing_{index + 1}.jpg"),
                order=index + 1,
            )

        with self.assertRaises(ProductMaximumImagesError) as context:
            add_product_image(
                product_id=self.product.id,
                images=[self._make_image("extra.jpg")],
            )

        self.assertEqual(context.exception.max_images, ProductImageRules.MAX_IMAGES_ALLOWED)

    def test_add_product_image_continues_order_after_existing_images(self):
        """Ensure add_product_image continues sequential order after existing images."""
        ProductImage.objects.create(
            product=self.product,
            image=self._make_image("existing1.jpg"),
            order=1,
        )
        ProductImage.objects.create(
            product=self.product,
            image=self._make_image("existing2.jpg"),
            order=2,
        )

        created_images = add_product_image(
            product_id=self.product.id,
            images=[
                self._make_image("new1.jpg"),
                self._make_image("new2.jpg"),
            ],
        )

        self.assertEqual(created_images[0].order, 3)
        self.assertEqual(created_images[1].order, 4)

    def test_add_product_image_assigns_sequential_order_for_bulk_upload(self):
        """Ensure add_product_image assigns sequential order during bulk creation."""
        created_images = add_product_image(
            product_id=self.product.id,
            images=[
                self._make_image("bulk1.jpg"),
                self._make_image("bulk2.jpg"),
                self._make_image("bulk3.jpg"),
                self._make_image("bulk4.jpg"),
            ],
        )

        orders = [image.order for image in created_images]

        self.assertEqual(orders, [1, 2, 3, 4])

    def test_add_product_image_allows_upload_up_to_maximum_limit(self):
        """Ensure add_product_image allows uploads exactly up to the maximum limit."""
        created_images = add_product_image(
            product_id=self.product.id,
            images=[
                self._make_image(f"image_{index + 1}.jpg")
                for index in range(ProductImageRules.MAX_IMAGES_ALLOWED)
            ],
        )

        self.assertEqual(len(created_images), ProductImageRules.MAX_IMAGES_ALLOWED)
        self.assertEqual(ProductImage.objects.filter(product=self.product).count(), ProductImageRules.MAX_IMAGES_ALLOWED)


class ValidateProductMinimumImagesTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="images@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Images User",
        )

        self.product = Product.objects.create(
            name="Studio Microphone",
            product_type=Product.MICROPHONE,
            brand="Shure",
            sold_by=self.user,
            description="Microphone description",
            technical_information="Professional audio specs",
            price=Decimal("899.90"),
            is_active=True,
        )

    def _make_image(self, name):
        """Create a valid uploaded image file for tests."""
        return SimpleUploadedFile(
            name,
            b"filecontent",
            content_type="image/jpeg",
        )

    def test_validate_product_minimum_images_raises_error_when_below_minimum(self):
        """Ensure validate_product_minimum_images raises error when image count is below minimum."""
        ProductImage.objects.create(
            product=self.product,
            image=self._make_image("image1.jpg"),
            order=1,
        )
        ProductImage.objects.create(
            product=self.product,
            image=self._make_image("image2.jpg"),
            order=2,
        )

        with self.assertRaises(ProductMinimumImagesError):
            validate_product_minimum_images(self.product)

    def test_validate_product_minimum_images_passes_when_equal_to_minimum(self):
        """Ensure validate_product_minimum_images passes when image count equals the minimum."""
        for index in range(ProductImageRules.MIN_IMAGES_REQUIRED):
            ProductImage.objects.create(
                product=self.product,
                image=self._make_image(f"image_{index + 1}.jpg"),
                order=index + 1,
            )

        validate_product_minimum_images(self.product)

    def test_validate_product_minimum_images_passes_when_above_minimum(self):
        """Ensure validate_product_minimum_images passes when image count is above the minimum."""
        for index in range(ProductImageRules.MIN_IMAGES_REQUIRED + 1):
            ProductImage.objects.create(
                product=self.product,
                image=self._make_image(f"image_{index + 1}.jpg"),
                order=index + 1,
            )

        validate_product_minimum_images(self.product)

    def test_validate_product_minimum_images_raises_error_when_no_images_exist(self):
        """Ensure validate_product_minimum_images raises error when product has no images."""
        with self.assertRaises(ProductMinimumImagesError):
            validate_product_minimum_images(self.product)