from django.contrib.auth import get_user_model

from rest_framework import serializers

from ech.products.models import Product
from ech.reviews.models import (
    Review,
    ReviewLifecycle,
    ReviewEvent,
)
from ech.reviews.services.review_creation_service import (
    ReviewsCreationService,
)
from ech.reviews.services.review_update_service import (
    ReviewsUpdateService,
)
from ech.reviews.services.review_cancellation_service import (
    ReviewsCancellationService,
)
from ech.reviews.services.review_moderation_service import (
    ReviewsModerationService,
)
from ech.reviews.constants.constants import (
    REVIEW_ACTION_APPROVE,
    REVIEW_ACTION_REJECT,
    REVIEW_ACTION_HIDE,
    REVIEW_ACTION_RESTORE,
    REVIEW_RATING_MIN,
    REVIEW_RATING_MAX,
)
from ech.reviews.selectors import get_product_review_summary


User = get_user_model()


class ReviewCustomerSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for review customer data.
    Suitable for authenticated and management responses.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "user_name",
            "user_email",
        ]


class ReviewPublicCustomerSerializer(serializers.ModelSerializer):
    """
    Public-safe serializer for customer data exposed in public review endpoints.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "user_name",
        ]


class ReviewProductSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product data embedded in review responses.
    """

    main_image = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "product_type",
            "main_image",
        ]


class ReviewLifecycleSerializer(serializers.ModelSerializer):
    """
    Serializer for review lifecycle timestamps.
    """

    class Meta:
        model = ReviewLifecycle
        fields = [
            "approved_at",
            "rejected_at",
            "hidden_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]


class ReviewEventSerializer(serializers.ModelSerializer):
    """
    Serializer for review audit events.
    """

    performed_by_name = serializers.CharField(
        source="performed_by.user_name",
        read_only=True,
    )
    performed_by_email = serializers.CharField(
        source="performed_by.user_email",
        read_only=True,
    )

    class Meta:
        model = ReviewEvent
        fields = [
            "id",
            "event_type",
            "performed_by",
            "performed_by_name",
            "performed_by_email",
            "metadata",
            "created_at",
        ]


class CreateReviewSerializer(serializers.Serializer):
    """
    Serializer responsible for validating review creation payload
    and delegating business logic to ReviewsCreationService.
    """

    product_id = serializers.UUIDField()
    rating = serializers.IntegerField(
        min_value=REVIEW_RATING_MIN,
        max_value=REVIEW_RATING_MAX,
    )
    title = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    idempotency_key = serializers.UUIDField(required=False)
    is_verified_purchase = serializers.BooleanField(
        required=False,
        default=False,
    )

    def validate_product_id(self, value):
        """
        Validate that the referenced product exists.
        """
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product not found.")
        return value

    def validate(self, attrs):
        """
        Resolve the product instance for service-layer consumption.
        """
        product = Product.objects.filter(id=attrs["product_id"]).first()

        if product is None:
            raise serializers.ValidationError(
                {"product_id": "Product not found."}
            )

        attrs["product"] = product
        return attrs

    def create(self, validated_data):
        """
        Create a new review using the service layer.
        """
        request = self.context["request"]

        return ReviewsCreationService.create_review(
            customer=request.user,
            product=validated_data["product"],
            rating=validated_data["rating"],
            title=validated_data.get("title", ""),
            comment=validated_data.get("comment", ""),
            idempotency_key=validated_data.get("idempotency_key"),
            is_verified_purchase=validated_data.get(
                "is_verified_purchase",
                False,
            ),
        )


class ReviewUpdateSerializer(serializers.Serializer):
    """
    Serializer responsible for validating partial review update payload
    and delegating business logic to ReviewsUpdateService.
    """

    rating = serializers.IntegerField(
        min_value=REVIEW_RATING_MIN,
        max_value=REVIEW_RATING_MAX,
        required=False,
    )
    title = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        """
        Ensure at least one editable field is provided.
        """
        if not attrs:
            raise serializers.ValidationError(
                "At least one field must be provided for update."
            )
        return attrs

    def create(self, validated_data):
        """
        Update a review through the service layer.
        """
        review = validated_data["review"]
        performed_by = validated_data.get("performed_by")

        update_kwargs = {}

        for field in ("rating", "title", "comment"):
            if field in validated_data:
                update_kwargs[field] = validated_data[field]

        return ReviewsUpdateService.update_review(
            review_id=review.id,
            performed_by=performed_by,
            **update_kwargs,
        )


class ReviewCancelSerializer(serializers.Serializer):
    """
    Serializer responsible for validating review cancellation payload
    and delegating business logic to ReviewsCancellationService.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def create(self, validated_data):
        """
        Cancel a review through the service layer.
        """
        review = validated_data["review"]
        performed_by = validated_data.get("performed_by")

        return ReviewsCancellationService.cancel_review(
            review_id=review.id,
            performed_by=performed_by,
            reason=validated_data.get("reason", ""),
        )


class ReviewModerationSerializer(serializers.Serializer):
    """
    Serializer responsible for validating moderation payload
    and delegating business logic to ReviewsModerationService.
    """

    action = serializers.ChoiceField(
        choices=[
            REVIEW_ACTION_APPROVE,
            REVIEW_ACTION_REJECT,
            REVIEW_ACTION_HIDE,
            REVIEW_ACTION_RESTORE,
        ],
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def create(self, validated_data):
        """
        Moderate a review through the service layer.
        """
        review = validated_data["review"]
        performed_by = validated_data.get("performed_by")

        return ReviewsModerationService.moderate_review(
            review_id=review.id,
            action=validated_data["action"],
            performed_by=performed_by,
            reason=validated_data.get("reason", ""),
        )


class ReviewListSerializer(serializers.ModelSerializer):
    """
    Serializer used for authenticated customer review list endpoints.
    Suitable for customer dashboards.
    """

    product = ReviewProductSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "rating",
            "title",
            "comment",
            "status",
            "is_verified_purchase",
            "moderation_reason",
            "moderated_at",
            "created_at",
            "updated_at",
        ]


class ReviewDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for authenticated customer review detail endpoints.
    """

    customer = ReviewCustomerSerializer(read_only=True)
    product = ReviewProductSerializer(read_only=True)
    lifecycle = ReviewLifecycleSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "customer",
            "product",
            "rating",
            "title",
            "comment",
            "status",
            "is_verified_purchase",
            "moderated_by",
            "moderation_reason",
            "moderated_at",
            "lifecycle",
            "created_at",
            "updated_at",
        ]


class ReviewManagementListSerializer(serializers.ModelSerializer):
    """
    Serializer used for staff review management list endpoints.
    Optimized for management dashboards.
    """

    customer = ReviewCustomerSerializer(read_only=True)
    product = ReviewProductSerializer(read_only=True)
    moderated_by_name = serializers.CharField(
        source="moderated_by.user_name",
        read_only=True,
    )
    moderated_by_email = serializers.CharField(
        source="moderated_by.user_email",
        read_only=True,
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "customer",
            "product",
            "rating",
            "title",
            "status",
            "is_verified_purchase",
            "moderated_by",
            "moderated_by_name",
            "moderated_by_email",
            "moderated_at",
            "created_at",
            "updated_at",
        ]


class ReviewManagementDetailSerializer(serializers.ModelSerializer):
    """
    Serializer used for staff review detail endpoints.
    """

    customer = ReviewCustomerSerializer(read_only=True)
    product = ReviewProductSerializer(read_only=True)
    lifecycle = ReviewLifecycleSerializer(read_only=True)
    events = ReviewEventSerializer(many=True, read_only=True)
    moderated_by_name = serializers.CharField(
        source="moderated_by.user_name",
        read_only=True,
    )
    moderated_by_email = serializers.CharField(
        source="moderated_by.user_email",
        read_only=True,
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "customer",
            "product",
            "rating",
            "title",
            "comment",
            "status",
            "idempotency_key",
            "is_verified_purchase",
            "moderated_by",
            "moderated_by_name",
            "moderated_by_email",
            "moderation_reason",
            "moderated_at",
            "lifecycle",
            "events",
            "created_at",
            "updated_at",
        ]


class ProductPublicReviewSerializer(serializers.ModelSerializer):
    """
    Serializer used for public product review listing endpoints.
    Restricted to publicly visible review data.
    """

    customer = ReviewPublicCustomerSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "customer",
            "rating",
            "title",
            "comment",
            "is_verified_purchase",
            "created_at",
        ]


class ProductReviewSummarySerializer(serializers.Serializer):
    """
    Serializer for aggregated product review summary responses.
    """

    product_id = serializers.UUIDField(read_only=True)
    average_rating = serializers.FloatField(
        read_only=True,
        allow_null=True,
    )
    total_reviews = serializers.IntegerField(read_only=True)
    rating_distribution = serializers.DictField(read_only=True)
    verified_reviews = serializers.IntegerField(read_only=True)

    @staticmethod
    def build_summary(product):
        """
        Build summary payload for a product using selector aggregation.
        """
        return get_product_review_summary(product)