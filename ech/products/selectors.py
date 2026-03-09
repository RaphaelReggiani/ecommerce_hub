from django.db.models import Q

from ech.products.models import Product


def get_product_by_id(product_id):
    """
    Returns a product by its ID.
    """
    return (
        Product.objects
        .select_related("sold_by")
        .prefetch_related("images")
        .filter(id=product_id)
        .first()
    )


def get_active_product_by_id(product_id):
    """
    Returns an active product by its ID.
    """
    return (
        Product.objects
        .select_related("sold_by")
        .prefetch_related("images")
        .filter(id=product_id, is_active=True)
        .first()
    )


def get_all_active_products():
    """
    Returns all active products.
    """
    return (
        Product.objects
        .filter(is_active=True)
        .select_related("sold_by")
        .prefetch_related("images")
        .order_by("-created_at")
    )


def get_products_by_type(product_type):
    """
    Returns active products filtered by product type.
    """
    return (
        Product.objects
        .filter(
            product_type=product_type,
            is_active=True
        )
        .select_related("sold_by")
        .prefetch_related("images")
        .order_by("-created_at")
    )


def get_products_with_discount():
    """
    Returns all active products that have a discount price.
    """
    return (
        Product.objects
        .filter(
            is_active=True,
            discount_price__isnull=False
        )
        .select_related("sold_by")
        .prefetch_related("images")
        .order_by("-created_at")
    )


def search_products(search_term):
    """
    Searches products by name or brand.
    """
    return (
        Product.objects
        .filter(
            Q(name__icontains=search_term) |
            Q(brand__icontains=search_term),
            is_active=True
        )
        .select_related("sold_by")
        .prefetch_related("images")
        .order_by("-created_at")
    )


def get_products_created_by_user(user):
    """
    Returns products created by a specific user.
    Useful for admin dashboards.
    """
    return (
        Product.objects
        .filter(sold_by=user)
        .prefetch_related("images")
        .order_by("-created_at")
    )


def get_available_products():
    """
    Returns products that are active and have inventory available.
    """
    return (
        Product.objects
        .filter(
            is_active=True,
            inventory__gt=0
        )
        .select_related("sold_by")
        .prefetch_related("images")
        .order_by("-created_at")
    )