from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from ech.users.models import (
    CustomUser,
)

from ech.products.models import (
    Product, 
    ProductImage,
)
from ech.products.services.product_image_service import (
    add_product_image,
    validate_product_minimum_images,
)

from ech.products.constants.constants import (
    ProductType, 
    ProductImageRules,
)
from ech.products.exceptions import (
    ProductNotFoundError,
    ProductMinimumImagesError,
)

from ech.users.constants.constants import (
    CORPORATE_EMAIL_DOMAIN,
)


User = get_user_model()


class ProductImageServiceTestCase(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            email=f"ops{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            user_name="ops_user",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
        )

        self.product = Product.objects.create(
            name="Gaming Keyboard",
            product_type=ProductType.CHOICES[0][0],
            brand="Razer",
            sold_by=self.user,
            description="Mechanical keyboard",
            technical_information="RGB switches",
            price=Decimal("500.00"),
        )

    def _create_test_image(self, name="test.jpg"):
        """
        Helper to create fake uploaded images.
        """

        return SimpleUploadedFile(
            name=name,
            content=b"file_content",
            content_type="image/jpeg",
        )

    def test_add_single_product_image(self):
        """
        Should successfully add one image.
        """

        image = self._create_test_image()

        result = add_product_image(
            product_id=self.product.id,
            images=[image],
        )

        self.assertEqual(len(result), 1)

        image_obj = ProductImage.objects.first()

        self.assertEqual(image_obj.product, self.product)
        self.assertEqual(image_obj.order, 1)

    def test_add_multiple_product_images(self):
        """
        Should correctly add multiple images.
        """

        images = [
            self._create_test_image("1.jpg"),
            self._create_test_image("2.jpg"),
            self._create_test_image("3.jpg"),
        ]

        result = add_product_image(
            product_id=self.product.id,
            images=images,
        )

        self.assertEqual(len(result), 3)

        self.assertEqual(ProductImage.objects.count(), 3)

    def test_image_order_is_sequential(self):
        """
        Order should increase sequentially.
        """

        images = [
            self._create_test_image("1.jpg"),
            self._create_test_image("2.jpg"),
        ]

        add_product_image(
            product_id=self.product.id,
            images=images,
        )

        orders = list(
            ProductImage.objects.values_list("order", flat=True)
        )

        self.assertEqual(orders, [1, 2])

    def test_order_continues_when_images_already_exist(self):
        """
        If images already exist, order should continue.
        """

        ProductImage.objects.create(
            product=self.product,
            image=self._create_test_image("existing.jpg"),
            order=1,
        )

        new_images = [
            self._create_test_image("new1.jpg"),
            self._create_test_image("new2.jpg"),
        ]

        add_product_image(
            product_id=self.product.id,
            images=new_images,
        )

        orders = list(
            ProductImage.objects.values_list("order", flat=True)
        )

        self.assertEqual(orders, [1, 2, 3])

    def test_add_images_product_not_found(self):
        """
        Should raise error if product does not exist.
        """

        image = self._create_test_image()

        with self.assertRaises(ProductNotFoundError):

            add_product_image(
                product_id=999,
                images=[image],
            )

    def test_validate_minimum_images_success(self):
        """
        Should pass when product has minimum images.
        """

        required = ProductImageRules.MIN_IMAGES_REQUIRED

        for i in range(required):
            ProductImage.objects.create(
                product=self.product,
                image=self._create_test_image(f"{i}.jpg"),
                order=i + 1,
            )

        validate_product_minimum_images(self.product)

    def test_validate_minimum_images_failure(self):
        """
        Should raise error when images are below minimum.
        """

        ProductImage.objects.create(
            product=self.product,
            image=self._create_test_image("only.jpg"),
            order=1,
        )

        with self.assertRaises(ProductMinimumImagesError):

            validate_product_minimum_images(self.product)

    def test_cannot_exceed_maximum_images(self):
        """
        Should raise error when exceeding maximum images allowed.
        """

        from ech.products.constants.constants import ProductImageRules
        from ech.products.exceptions import ProductMaximumImagesError

        max_images = ProductImageRules.MAX_IMAGES_ALLOWED

        for i in range(max_images):
            ProductImage.objects.create(
                product=self.product,
                image=self._create_test_image(f"{i}.jpg"),
                order=i + 1,
            )

        new_image = self._create_test_image("extra.jpg")

        with self.assertRaises(ProductMaximumImagesError):

            add_product_image(
                product_id=self.product.id,
                images=[new_image],
            )