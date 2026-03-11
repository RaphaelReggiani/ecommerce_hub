import uuid
from django.db import models
from django.conf import settings
from django.core.validators import (
    MinValueValidator, 
    FileExtensionValidator,
)

from ech.products.constants.constants import (
    LABEL_PHONE,
    LABEL_EARPHONE,
    LABEL_HEADSET,
    LABEL_MOUSE,
    LABEL_KEYBOARD,
    LABEL_MICROPHONE,
    LABEL_EVENT_PRODUCT_CREATED,
    LABEL_EVENT_PRODUCT_UPDATED,
    LABEL_EVENT_PRODUCT_DELETED,
    LABEL_EVENT_PRODUCT_IMAGE_UPLOADED,
)
from ech.products.constants.storage import (
    PRODUCT_IMAGES_UPLOAD_PATH,
)

from ech.products.constants.inventory import (
    DEFAULT_PRODUCT_INVENTORY,
)


class Product(models.Model):
    """
    Main product model.
    Stores the core product information used across the application.[
    """

    PHONE = "PHONE"
    EARPHONE = "EARPHONE"
    HEADSET = "HEADSET"
    MOUSE = "MOUSE"
    KEYBOARD = "KEYBOARD"
    MICROPHONE = "MICROPHONE"

    PRODUCT_CHOICES = [
        (PHONE, LABEL_PHONE),
        (EARPHONE, LABEL_EARPHONE),
        (HEADSET, LABEL_HEADSET),
        (MOUSE, LABEL_MOUSE),
        (KEYBOARD, LABEL_KEYBOARD),
        (MICROPHONE, LABEL_MICROPHONE),
    ]



    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=255
    )

    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_CHOICES,
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
    

class ProductEventLog(models.Model):
    """
    Stores audit events related to product lifecycle.
    Useful for debugging, compliance and operational monitoring.
    """

    EVENT_PRODUCT_CREATED = "product_created"
    EVENT_PRODUCT_UPDATED = "product_updated"
    EVENT_PRODUCT_DELETED = "product_deleted"
    EVENT_PRODUCT_IMAGE_UPLOADED = "product_image_uploaded"

    EVENT_CHOICES = [
        (EVENT_PRODUCT_CREATED, LABEL_EVENT_PRODUCT_CREATED),
        (EVENT_PRODUCT_UPDATED, LABEL_EVENT_PRODUCT_UPDATED),
        (EVENT_PRODUCT_DELETED, LABEL_EVENT_PRODUCT_DELETED),
        (EVENT_PRODUCT_IMAGE_UPLOADED, LABEL_EVENT_PRODUCT_IMAGE_UPLOADED),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="event_logs"
    )

    event_type = models.CharField(
        max_length=40,
        choices=EVENT_CHOICES,
        db_index=True
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="product_events"
    )

    metadata = models.JSONField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["product", "created_at"],
                name="prod_evt_prod_created_idx"
            )
        ]

    def __str__(self):
        return f"{self.product_id} - {self.event_type}"