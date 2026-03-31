from django.db.models import Avg, Count, Q

from ech.reviews.models import Review, ReviewLifecycle, ReviewEvent
from ech.reviews.exceptions import ReviewNotFoundException


def get_review_by_id(review_id):
    """
    Retrieve a review by its ID.

    Raises:
        ReviewNotFoundException: if the review does not exist.
    """
    try:
        return Review.objects.select_related(
            "customer",
            "product",
            "moderated_by",
            "lifecycle",
        ).get(id=review_id)
    except Review.DoesNotExist as exc:
        raise ReviewNotFoundException() from exc


def get_review_by_id_for_customer(review_id, customer):
    """
    Retrieve a review by ID restricted to its owner.

    Raises:
        ReviewNotFoundException: if the review does not exist
        or does not belong to the given customer.
    """
    try:
        return Review.objects.select_related(
            "customer",
            "product",
            "moderated_by",
            "lifecycle",
        ).get(id=review_id, customer=customer)
    except Review.DoesNotExist as exc:
        raise ReviewNotFoundException() from exc


def get_review_by_idempotency_key(idempotency_key):
    """
    Retrieve a review by idempotency key.

    Returns:
        Review | None
    """
    if not idempotency_key:
        return None

    return (
        Review.objects.select_related(
            "customer",
            "product",
            "moderated_by",
            "lifecycle",
        )
        .filter(idempotency_key=idempotency_key)
        .first()
    )


def get_review_by_customer_and_product(customer, product):
    """
    Retrieve a review by customer and product.

    Returns:
        Review | None
    """
    return (
        Review.objects.select_related(
            "customer",
            "product",
            "moderated_by",
            "lifecycle",
        )
        .filter(customer=customer, product=product)
        .first()
    )


def get_review_lifecycle(review):
    """
    Retrieve lifecycle object for a review.

    Raises:
        ReviewNotFoundException: if lifecycle does not exist.
    """
    try:
        return ReviewLifecycle.objects.get(review=review)
    except ReviewLifecycle.DoesNotExist as exc:
        raise ReviewNotFoundException("Review lifecycle not found.") from exc


def list_reviews_for_customer(customer):
    """
    List all reviews created by a given customer.
    """
    return Review.objects.select_related(
        "product",
        "moderated_by",
        "lifecycle",
    ).filter(customer=customer)


def list_reviews_for_management():
    """
    List all reviews for staff management dashboards.
    """
    return Review.objects.select_related(
        "customer",
        "product",
        "moderated_by",
        "lifecycle",
    ).all()


def list_reviews_by_product(product):
    """
    List all reviews for a given product.
    """
    return Review.objects.select_related(
        "customer",
        "moderated_by",
        "lifecycle",
    ).filter(product=product)


def list_public_reviews_by_product(product):
    """
    List publicly visible reviews for a product.

    Public reviews are restricted to approved reviews only.
    """
    return Review.objects.select_related(
        "customer",
    ).filter(
        product=product,
        status=Review.REVIEW_STATUS_APPROVED,
    )


def list_reviews_by_status(status_value):
    """
    List reviews filtered by status.
    """
    return Review.objects.select_related(
        "customer",
        "product",
        "moderated_by",
        "lifecycle",
    ).filter(status=status_value)


def list_reviews_by_rating(rating):
    """
    List reviews filtered by rating value.
    """
    return Review.objects.select_related(
        "customer",
        "product",
        "moderated_by",
        "lifecycle",
    ).filter(rating=rating)


def list_verified_purchase_reviews():
    """
    List reviews marked as verified purchase.
    """
    return Review.objects.select_related(
        "customer",
        "product",
        "moderated_by",
        "lifecycle",
    ).filter(is_verified_purchase=True)


def list_review_events(review):
    """
    List all audit events related to a review.
    """
    return ReviewEvent.objects.select_related(
        "performed_by",
    ).filter(review=review)


def get_product_review_summary(product):
    """
    Return aggregated review summary for a given product.

    Only approved reviews are included in the public summary.
    """
    approved_reviews = Review.objects.filter(
        product=product,
        status=Review.REVIEW_STATUS_APPROVED,
    )

    aggregates = approved_reviews.aggregate(
        average_rating=Avg("rating"),
        total_reviews=Count("id"),
        rating_1=Count("id", filter=Q(rating=1)),
        rating_2=Count("id", filter=Q(rating=2)),
        rating_3=Count("id", filter=Q(rating=3)),
        rating_4=Count("id", filter=Q(rating=4)),
        rating_5=Count("id", filter=Q(rating=5)),
        verified_reviews=Count("id", filter=Q(is_verified_purchase=True)),
    )

    return {
        "product_id": product.id,
        "average_rating": aggregates["average_rating"],
        "total_reviews": aggregates["total_reviews"],
        "rating_distribution": {
            1: aggregates["rating_1"],
            2: aggregates["rating_2"],
            3: aggregates["rating_3"],
            4: aggregates["rating_4"],
            5: aggregates["rating_5"],
        },
        "verified_reviews": aggregates["verified_reviews"],
    }