from rest_framework.permissions import BasePermission

from ech.reviews.constants.roles_management import (
    ALLOWED_REVIEWS_ROLES,
)
from ech.reviews.constants.messages import (
    REVIEW_MODERATION_NOT_ALLOWED,
    REVIEW_UPDATE_NOT_ALLOWED,
)


class IsReviewOwner(BasePermission):
    """
    Allows access only to the owner of the review.
    """

    message = REVIEW_UPDATE_NOT_ALLOWED

    def has_object_permission(self, request, view, obj):
        return obj.customer_id == request.user.id


class CanManageReviews(BasePermission):
    """
    Allows access only to users with management roles
    for the reviews domain.
    """

    message = REVIEW_MODERATION_NOT_ALLOWED

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.user_role in ALLOWED_REVIEWS_ROLES


class IsReviewOwnerOrCanManageReviews(BasePermission):
    """
    Allows access to the review owner or users who can manage reviews.
    Useful for shared review access scenarios.
    """

    message = REVIEW_UPDATE_NOT_ALLOWED

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if obj.customer_id == user.id:
            return True

        return user.user_role in ALLOWED_REVIEWS_ROLES