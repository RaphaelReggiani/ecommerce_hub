from django.db import transaction

from ech.reviews.models import (
    Review,
)
from ech.reviews.exceptions import (
    InvalidReviewModerationActionException,
    ReviewModerationNotAllowedException,
)
from ech.reviews.selectors import get_review_by_id
from ech.reviews.services.review_status_service import ReviewsStatusService

from ech.reviews.constants.constants import (
    REVIEW_ACTION_APPROVE,
    REVIEW_ACTION_REJECT,
    REVIEW_ACTION_HIDE,
    REVIEW_ACTION_RESTORE,
    REVIEW_MODERATION_ACTIONS,
)


class ReviewsModerationService:
    """
    Service responsible for review moderation actions.

    Moderation actions are delegated to ReviewsStatusService
    after validating that the requested action is allowed
    for the current review state.
    """

    ACTION_TO_STATUS = {
        REVIEW_ACTION_APPROVE: Review.REVIEW_STATUS_APPROVED,
        REVIEW_ACTION_REJECT: Review.REVIEW_STATUS_REJECTED,
        REVIEW_ACTION_HIDE: Review.REVIEW_STATUS_HIDDEN,
        REVIEW_ACTION_RESTORE: Review.REVIEW_STATUS_APPROVED,
    }

    @staticmethod
    def _validate_action(action):
        if action not in REVIEW_MODERATION_ACTIONS:
            raise InvalidReviewModerationActionException()

    @staticmethod
    def _validate_restore(review):
        if review.status != Review.REVIEW_STATUS_HIDDEN:
            raise ReviewModerationNotAllowedException(
                "Only hidden reviews can be restored."
            )

    @staticmethod
    def _validate_approve(review):
        if review.status not in {
            Review.REVIEW_STATUS_PENDING,
            Review.REVIEW_STATUS_REJECTED,
            Review.REVIEW_STATUS_HIDDEN,
        }:
            raise ReviewModerationNotAllowedException(
                "This review cannot be approved from its current status."
            )

    @staticmethod
    def _validate_reject(review):
        if review.status not in {
            Review.REVIEW_STATUS_PENDING,
        }:
            raise ReviewModerationNotAllowedException(
                "Only pending reviews can be rejected."
            )

    @staticmethod
    def _validate_hide(review):
        if review.status not in {
            Review.REVIEW_STATUS_APPROVED,
        }:
            raise ReviewModerationNotAllowedException(
                "Only approved reviews can be hidden."
            )

    @classmethod
    def _validate_action_for_review(cls, review, action):
        if action == REVIEW_ACTION_RESTORE:
            cls._validate_restore(review)
            return

        if action == REVIEW_ACTION_APPROVE:
            cls._validate_approve(review)
            return

        if action == REVIEW_ACTION_REJECT:
            cls._validate_reject(review)
            return

        if action == REVIEW_ACTION_HIDE:
            cls._validate_hide(review)
            return

        raise InvalidReviewModerationActionException()

    @classmethod
    @transaction.atomic
    def moderate_review(
        cls,
        *,
        review_id,
        action,
        performed_by=None,
        reason="",
        metadata=None,
    ):
        """
        Execute a moderation action for a review.

        Supported actions:
        - approve
        - reject
        - hide
        - restore
        """

        cls._validate_action(action)

        review = get_review_by_id(review_id)

        cls._validate_action_for_review(review, action)

        new_status = cls.ACTION_TO_STATUS[action]

        return ReviewsStatusService.change_status(
            review_id=review.id,
            new_status=new_status,
            performed_by=performed_by,
            moderation_reason=reason,
            metadata={
                "moderation_action": action,
                **(metadata or {}),
            },
        )