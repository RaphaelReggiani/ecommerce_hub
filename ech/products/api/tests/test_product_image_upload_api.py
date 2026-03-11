from decimal import Decimal
from io import BytesIO
from PIL import Image

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase
from rest_framework import status

from ech.products.models import Product

from ech.products.constants.rules import ProductImageRules

from ech.users.constants.constants import (
    CORPORATE_EMAIL_DOMAIN,
)

from ech.users.models import (
    CustomUser,
)

User = get_user_model()


class ProductImageUploadAPITestCase(APITestCase):

    def setUp(self):

        self.manager = User.objects.create_user(
            email=f"ops{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            user_name="ops_user",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
        )

        self.customer = User.objects.create_user(
            email="customer@gmail.com",
            password="StrongPassword123",
            user_name="customer_user",
            role=CustomUser.ROLE_CUSTOMER_USER,
        )

        self.product = Product.objects.create(
            name="Gaming Monitor",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="LG",
            sold_by=self.manager,
            description="Monitor",
            technical_information="144Hz",
            price=Decimal("1500.00"),
        )

    def _image(self):

        file = BytesIO()
        image = Image.new("RGB", (100, 100))
        image.save(file, "JPEG")
        file.seek(0)

        return SimpleUploadedFile(
            "test.jpg",
            file.read(),
            content_type="image/jpeg",
        )

    def test_upload_image_manager(self):

        self.client.force_authenticate(self.manager)

        url = reverse("product-image-upload", args=[str(self.product.id)])

        data = {
            "image": self._image(),
            "order": 1,
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_upload_image_forbidden(self):

        self.client.force_authenticate(self.customer)

        url = reverse("product-image-upload", args=[str(self.product.id)])

        data = {
            "image": self._image(),
            "order": 1,
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_image_limit_exceeded(self):
        """
        Uploading more images than allowed should fail.
        """

        self.client.force_authenticate(self.manager)

        url = reverse("product-image-upload", args=[str(self.product.id)])


        for i in range(ProductImageRules.MAX_IMAGES_ALLOWED):

            image = SimpleUploadedFile(
                f"test{i}.jpg",
                b"file_content",
                content_type="image/jpeg",
            )

            self.client.post(
                url,
                {"image": image, "order": i + 1},
                format="multipart",
            )

        extra_image = SimpleUploadedFile(
            "extra.jpg",
            b"file_content",
            content_type="image/jpeg",
        )

        response = self.client.post(
            url,
            {"image": extra_image, "order": 99},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)