import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ech.products.models import Product

from ech.reviews.constants.constants import (
    LABEL_REVIEW_STATUS_PENDING,
    LABEL_REVIEW_STATUS_APPROVED,
    LABEL_REVIEW_STATUS_REJECTED,
    LABEL_REVIEW_STATUS_HIDDEN,
    LABEL_REVIEW_STATUS_CANCELLED,
)


class Review(models.Model):
    """
    Main Review model (Aggregate Root).

    Represents a customer's review for a product.
    All related entities (lifecycle, events, etc.)
    belong to this aggregate.
    """

    """
    Review status choices.
    """

    REVIEW_STATUS_PENDING = "pending"
    REVIEW_STATUS_APPROVED = "approved"
    REVIEW_STATUS_REJECTED = "rejected"
    REVIEW_STATUS_HIDDEN = "hidden"
    REVIEW_STATUS_CANCELLED = "cancelled"

    REVIEW_STATUS_CHOICES = [
        (REVIEW_STATUS_PENDING, LABEL_REVIEW_STATUS_PENDING),
        (REVIEW_STATUS_APPROVED, LABEL_REVIEW_STATUS_APPROVED),
        (REVIEW_STATUS_REJECTED, LABEL_REVIEW_STATUS_REJECTED),
        (REVIEW_STATUS_HIDDEN, LABEL_REVIEW_STATUS_HIDDEN),
        (REVIEW_STATUS_CANCELLED, LABEL_REVIEW_STATUS_CANCELLED),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reviews",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        db_index=True,
    )

    title = models.CharField(
        max_length=255,
        blank=True,
    )

    comment = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=32,
        choices=REVIEW_STATUS_CHOICES,
        default=REVIEW_STATUS_PENDING,
        db_index=True,
    )

    idempotency_key = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )

    is_verified_purchase = models.BooleanField(
        default=False,
        db_index=True,
    )

    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderated_reviews",
    )

    moderation_reason = models.TextField(
        blank=True,
    )

    moderated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "product"],
                name="unique_customer_product_review",
            ),
        ]
        indexes = [
            models.Index(
                fields=["product", "status", "created_at"],
                name="review_product_status_created_idx",
            ),
            models.Index(
                fields=["customer", "created_at"],
                name="review_customer_created_idx",
            ),
            models.Index(
                fields=["product", "rating"],
                name="review_product_rating_idx",
            ),
        ]

    def __str__(self):
        return f"Review {self.id} - {self.product_id}"


class ReviewLifecycle(models.Model):
    """
    Tracks lifecycle timestamps of a review.
    """

    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name="lifecycle",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    hidden_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Lifecycle for Review {self.review_id}"


class ReviewEvent(models.Model):
    """
    Stores audit events related to a review.
    Useful for operational monitoring and moderation traceability.
    """

    TYPE_CREATED = "review_created"
    TYPE_UPDATED = "review_updated"
    TYPE_APPROVED = "review_approved"
    TYPE_REJECTED = "review_rejected"
    TYPE_HIDDEN = "review_hidden"
    TYPE_RESTORED = "review_restored"
    TYPE_CANCELLED = "review_cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="events",
    )

    event_type = models.CharField(
        max_length=100,
        db_index=True,
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    metadata = models.JSONField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["review", "created_at"],
                name="reviewevent_review_created_idx",
            ),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.review_id}"