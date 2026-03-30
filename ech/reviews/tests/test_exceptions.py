from django.test import TestCase

from ech.reviews.constants.messages import (
    REVIEW_NOT_FOUND,
    REVIEW_CREATION_NOT_ALLOWED,
    REVIEW_UPDATE_NOT_ALLOWED,
    REVIEW_CANCELLATION_NOT_ALLOWED,
    REVIEW_MODERATION_NOT_ALLOWED,
    REVIEW_ALREADY_EXISTS_FOR_PRODUCT,
    INVALID_REVIEW_STATUS_TRANSITION,
    INVALID_REVIEW_ACTION,
    INVALID_REVIEW_RATING,
)
from ech.reviews.exceptions import (
    ReviewException,
    ReviewNotFoundException,
    ReviewPermissionDeniedException,
    ReviewCreationNotAllowedException,
    DuplicateReviewException,
    InvalidReviewRatingException,
    InvalidReviewStatusTransitionException,
    ReviewCancellationNotAllowedException,
    ReviewModerationNotAllowedException,
    InvalidReviewModerationActionException,
)


class ReviewExceptionsTestCase(TestCase):
    def test_base_review_exception_uses_default_message(self):
        """Use default message for base review exception."""
        exception = ReviewException()

        self.assertEqual(str(exception), "Review domain exception.")
        self.assertEqual(exception.message, "Review domain exception.")

    def test_base_review_exception_accepts_custom_message(self):
        """Allow custom message for base review exception."""
        exception = ReviewException("Custom review error.")

        self.assertEqual(str(exception), "Custom review error.")
        self.assertEqual(exception.message, "Custom review error.")

    def test_review_not_found_exception_uses_default_message(self):
        """Use default message for missing review."""
        exception = ReviewNotFoundException()

        self.assertEqual(str(exception), REVIEW_NOT_FOUND)

    def test_review_permission_denied_exception_uses_default_message(self):
        """Use default message for permission denial."""
        exception = ReviewPermissionDeniedException()

        self.assertEqual(str(exception), REVIEW_UPDATE_NOT_ALLOWED)

    def test_review_creation_not_allowed_exception_uses_default_message(self):
        """Use default message for invalid creation attempts."""
        exception = ReviewCreationNotAllowedException()

        self.assertEqual(str(exception), REVIEW_CREATION_NOT_ALLOWED)

    def test_duplicate_review_exception_uses_default_message(self):
        """Use default message for duplicate reviews."""
        exception = DuplicateReviewException()

        self.assertEqual(str(exception), REVIEW_ALREADY_EXISTS_FOR_PRODUCT)

    def test_invalid_review_rating_exception_uses_default_message(self):
        """Use default message for invalid review rating."""
        exception = InvalidReviewRatingException()

        self.assertEqual(str(exception), INVALID_REVIEW_RATING)

    def test_invalid_review_status_transition_exception_uses_default_message(self):
        """Use default message for invalid status transitions."""
        exception = InvalidReviewStatusTransitionException()

        self.assertEqual(str(exception), INVALID_REVIEW_STATUS_TRANSITION)

    def test_review_cancellation_not_allowed_exception_uses_default_message(self):
        """Use default message for invalid cancellation attempts."""
        exception = ReviewCancellationNotAllowedException()

        self.assertEqual(str(exception), REVIEW_CANCELLATION_NOT_ALLOWED)

    def test_review_moderation_not_allowed_exception_uses_default_message(self):
        """Use default message for invalid moderation attempts."""
        exception = ReviewModerationNotAllowedException()

        self.assertEqual(str(exception), REVIEW_MODERATION_NOT_ALLOWED)

    def test_invalid_review_moderation_action_exception_uses_default_message(self):
        """Use default message for invalid moderation actions."""
        exception = InvalidReviewModerationActionException()

        self.assertEqual(str(exception), INVALID_REVIEW_ACTION)

    def test_all_review_exceptions_inherit_from_base_review_exception(self):
        """Ensure all review exceptions inherit from ReviewException."""
        exceptions = [
            ReviewNotFoundException,
            ReviewPermissionDeniedException,
            ReviewCreationNotAllowedException,
            DuplicateReviewException,
            InvalidReviewRatingException,
            InvalidReviewStatusTransitionException,
            ReviewCancellationNotAllowedException,
            ReviewModerationNotAllowedException,
            InvalidReviewModerationActionException,
        ]

        for exception_class in exceptions:
            with self.subTest(exception_class=exception_class.__name__):
                self.assertTrue(issubclass(exception_class, ReviewException))