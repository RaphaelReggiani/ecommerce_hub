from django.db import models
from django.conf import settings
from django.core.validators import (
    MinValueValidator, 
    FileExtensionValidator,
)

from ech.products.constants.constants import ProductType
from ech.products.constants.storage import (
    PRODUCT_IMAGES_UPLOAD_PATH,
)

from ech.products.constants.inventory import (
    DEFAULT_PRODUCT_INVENTORY,
)


class Product(models.Model):
    """
    Main product model.
    Stores the core product information used across the application.
    """

    name = models.CharField(
        max_length=255
    )

    product_type = models.CharField(
        max_length=20,
        choices=ProductType.CHOICES,
        db_index=True
    )

    brand = models.CharField(
        max_length=120
    )

    sold_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="products_created"
    )

    description = models.TextField()

    technical_information = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["is_active", "-created_at"],
                name="product_active_created_idx"
            ),
            models.Index(
                fields=["sold_by"],
                name="product_seller_idx"
            ),
            models.Index(
                fields=["product_type", "is_active"],
                name="product_type_active_idx"
            ),
            models.Index(
                fields=["brand"],
                name="product_brand_idx"
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def has_discount(self):
        return (
            self.discount_price is not None
            and self.discount_price < self.price
        )

    @property
    def main_image(self):
        first_image = self.images.order_by("order").first()

        if first_image and first_image.image:
            return first_image.image.url

        return None

    @property
    def inventory(self):
        """
        Shortcut to access product inventory.
        """

        try:
            return self.inventory_record.quantity
        except ProductInventory.DoesNotExist:
            return 0


class ProductInventory(models.Model):
    """
    Stores product inventory separately from Product.
    This allows future expansion (warehouses, reservations, etc.).
    """

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory_record"
    )

    quantity = models.PositiveIntegerField(
        default=DEFAULT_PRODUCT_INVENTORY
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        indexes = [
            models.Index(
                fields=["product"],
                name="inventory_product_idx"
            )
        ]

    def __str__(self):
        return f"{self.product_id} inventory: {self.quantity}"
    

class ProductImage(models.Model):
    """
    Stores product images.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to=PRODUCT_IMAGES_UPLOAD_PATH,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"]
            )
        ]
    )

    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Defines the display order of the image."
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["order"]

        constraints = [
            models.UniqueConstraint(
                fields=["product", "order"],
                name="unique_product_image_order"
            )
        ]

    def __str__(self):
        return f"{self.product.name} - Image {self.order}"