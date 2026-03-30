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


class ReviewException(Exception):
    """
    Base exception for the reviews domain.
    """

    default_message = "Review domain exception."

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class ReviewNotFoundException(ReviewException):
    """
    Raised when a review cannot be found.
    """

    default_message = REVIEW_NOT_FOUND


class ReviewPermissionDeniedException(ReviewException):
    """
    Raised when a user does not have permission
    to access or manage a review.
    """

    default_message = REVIEW_UPDATE_NOT_ALLOWED


class ReviewCreationNotAllowedException(ReviewException):
    """
    Raised when a review cannot be created
    under the current business rules.
    """

    default_message = REVIEW_CREATION_NOT_ALLOWED


class DuplicateReviewException(ReviewException):
    """
    Raised when a customer tries to create
    more than one review for the same product.
    """

    default_message = REVIEW_ALREADY_EXISTS_FOR_PRODUCT


class InvalidReviewRatingException(ReviewException):
    """
    Raised when a review rating is outside
    the allowed range.
    """

    default_message = INVALID_REVIEW_RATING


class InvalidReviewStatusTransitionException(ReviewException):
    """
    Raised when a review status transition
    is not allowed.
    """

    default_message = INVALID_REVIEW_STATUS_TRANSITION


class ReviewCancellationNotAllowedException(ReviewException):
    """
    Raised when a review cannot be cancelled.
    """

    default_message = REVIEW_CANCELLATION_NOT_ALLOWED


class ReviewModerationNotAllowedException(ReviewException):
    """
    Raised when a moderation action is not allowed
    for the current user or current review state.
    """

    default_message = REVIEW_MODERATION_NOT_ALLOWED


class InvalidReviewModerationActionException(ReviewException):
    """
    Raised when an invalid moderation action is requested.
    """

    default_message = INVALID_REVIEW_ACTION