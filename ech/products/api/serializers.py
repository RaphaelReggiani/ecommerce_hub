from rest_framework import serializers

from ech.products.models import (
    Product,
    ProductImage,
)
from ech.products.services.product_creation_service import (
    create_product,
)
from ech.products.services.product_image_service import (
    add_product_image,
)

from ech.products.constants.messages import (
    MSG_ERROR_DISCOUNT_PRICE_MUST_BE_LOWER,
)


class ProductCreateSerializer(serializers.Serializer):
    """
    Serializer used to create a product.
    """

    name = serializers.CharField(max_length=255)
    product_type = serializers.CharField()
    brand = serializers.CharField(max_length=120)

    description = serializers.CharField()
    technical_information = serializers.CharField()

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True
    )

    inventory = serializers.IntegerField(
        min_value=0
    )

    def create(self, validated_data):
        """
        Delegates product creation to the service layer.
        """

        user = self.context["request"].user

        product = create_product(
            user=user,
            **validated_data
        )

        return product
    
    def validate(self, attrs):

        price = attrs.get("price")
        discount = attrs.get("discount_price")

        if discount is not None and discount >= price:
            raise serializers.ValidationError(MSG_ERROR_DISCOUNT_PRICE_MUST_BE_LOWER)

        return attrs


class ProductImageUploadSerializer(serializers.Serializer):
    """
    Serializer used to upload product images.
    """

    image = serializers.ImageField()
    order = serializers.IntegerField(
        min_value=1
    )

    def create(self, validated_data):
        """
        Delegates image creation to the service layer.
        """

        product = self.context["product"]

        product_images = add_product_image(
            product=product,
            **validated_data
        )

        return product_images


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer used to display product images.
    """

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "order",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer used to display product details.
    """

    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    inventory = serializers.IntegerField(
        read_only=True
    )

    main_image = serializers.CharField(
        read_only=True
    )

    has_discount = serializers.BooleanField(
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "product_type",
            "brand",
            "description",
            "technical_information",
            "price",
            "discount_price",
            "has_discount",
            "inventory",
            "main_image",
            "images",
            "created_at",
        ]