import logging
from datetime import datetime
from uuid import UUID


logger = logging.getLogger("ech.reviews")


class ReviewsLogService:
    """
    Structured logging service for reviews operations.

    This service centralizes audit-oriented logging for the reviews module,
    ensuring consistent payload structure across domain operations.
    """

    @staticmethod
    def _serialize_value(value):
        """
        Safely serialize values for structured logging.
        """
        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, datetime):
            return value.isoformat()

        return value

    @classmethod
    def _serialize_metadata(cls, metadata):
        """
        Safely serialize metadata dictionary values.
        """
        if not metadata:
            return {}

        return {
            key: cls._serialize_value(value)
            for key, value in metadata.items()
        }

    @classmethod
    def _build_payload(cls, *, action, review=None, performed_by=None, metadata=None):
        """
        Build a standardized structured logging payload.
        """
        return {
            "action": action,
            "review_id": cls._serialize_value(review.id) if review else None,
            "product_id": cls._serialize_value(review.product_id) if review else None,
            "customer_id": cls._serialize_value(review.customer_id) if review else None,
            "performed_by_id": (
                cls._serialize_value(performed_by.id)
                if performed_by else None
            ),
            "status": getattr(review, "status", None) if review else None,
            "metadata": cls._serialize_metadata(metadata),
        }

    @classmethod
    def log_review_created(cls, *, review, performed_by=None, metadata=None):
        logger.info(
            "review_created",
            extra={
                "payload": cls._build_payload(
                    action="review_created",
                    review=review,
                    performed_by=performed_by,
                    metadata=metadata,
                )
            },
        )

    @classmethod
    def log_review_updated(cls, *, review, performed_by=None, metadata=None):
        logger.info(
            "review_updated",
            extra={
                "payload": cls._build_payload(
                    action="review_updated",
                    review=review,
                    performed_by=performed_by,
                    metadata=metadata,
                )
            },
        )

    @classmethod
    def log_review_status_changed(cls, *, review, performed_by=None, metadata=None):
        logger.info(
            "review_status_changed",
            extra={
                "payload": cls._build_payload(
                    action="review_status_changed",
                    review=review,
                    performed_by=performed_by,
                    metadata=metadata,
                )
            },
        )

    @classmethod
    def log_review_cancelled(cls, *, review, performed_by=None, metadata=None):
        logger.info(
            "review_cancelled",
            extra={
                "payload": cls._build_payload(
                    action="review_cancelled",
                    review=review,
                    performed_by=performed_by,
                    metadata=metadata,
                )
            },
        )

    @classmethod
    def log_review_moderated(cls, *, review, performed_by=None, metadata=None):
        logger.info(
            "review_moderated",
            extra={
                "payload": cls._build_payload(
                    action="review_moderated",
                    review=review,
                    performed_by=performed_by,
                    metadata=metadata,
                )
            },
        )