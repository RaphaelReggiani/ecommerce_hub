import logging
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


logger = logging.getLogger(__name__)


class OrderLogService:
    """
    Structured logging service for order-related operations.

    This service provides application-level observability
    without changing domain behavior or persistence flow.
    """

    @classmethod
    def log_order_created(cls, *, order, metadata=None):
        logger.info(
            "order_created",
            extra=cls._build_payload(
                event="order_created",
                order=order,
                metadata=metadata,
            ),
        )

    @classmethod
    def log_order_creation_failed(
        cls,
        *,
        customer=None,
        idempotency_key=None,
        reason=None,
        metadata=None,
    ):
        logger.warning(
            "order_creation_failed",
            extra=cls._build_payload(
                event="order_creation_failed",
                customer=customer,
                idempotency_key=idempotency_key,
                reason=reason,
                metadata=metadata,
            ),
        )

    @classmethod
    def log_idempotency_replay(cls, *, order, idempotency_key=None, metadata=None):
        logger.info(
            "order_idempotency_replay",
            extra=cls._build_payload(
                event="order_idempotency_replay",
                order=order,
                idempotency_key=idempotency_key,
                metadata=metadata,
            ),
        )

    @classmethod
    def log_order_confirmed(cls, *, order, performed_by=None, metadata=None):
        logger.info(
            "order_confirmed",
            extra=cls._build_payload(
                event="order_confirmed",
                order=order,
                performed_by=performed_by,
                metadata=metadata,
            ),
        )

    @classmethod
    def log_order_processing_started(cls, *, order, performed_by=None, metadata=None):
        logger.info(
            "order_processing_started",
            extra=cls._build_payload(
                event="order_processing_started",
                order=order,
                performed_by=performed_by,
                metadata=metadata,
            ),
        )

    @classmethod
    def log_order_shipped(cls, *, order, performed_by=None, metadata=None):
        logger.info(
            "order_shipped",
            extra=cls._build_payload(
                event="order_shipped",
                order=order,
                performed_by=performed_by,
                metadata=metadata,
            ),
        )

    @classmethod
    def log_order_delivered(cls, *, order, performed_by=None, metadata=None):
        logger.info(
            "order_delivered",
            extra=cls._build_payload(
                event="order_delivered",
                order=order,
                performed_by=performed_by,
                metadata=metadata,
            ),
        )

    @classmethod
    def log_invalid_status_transition(
        cls,
        *,
        order,
        attempted_action,
        performed_by=None,
        reason=None,
        metadata=None,
    ):
        logger.warning(
            "order_invalid_status_transition",
            extra=cls._build_payload(
                event="order_invalid_status_transition",
                order=order,
                performed_by=performed_by,
                reason=reason,
                metadata={
                    "attempted_action": attempted_action,
                    **(metadata or {}),
                },
            ),
        )

    @classmethod
    def log_order_cancelled(cls, *, order, performed_by=None, metadata=None):
        logger.info(
            "order_cancelled",
            extra=cls._build_payload(
                event="order_cancelled",
                order=order,
                performed_by=performed_by,
                metadata=metadata,
            ),
        )

    @classmethod
    def log_cancellation_rejected(
        cls,
        *,
        order,
        performed_by=None,
        reason=None,
        metadata=None,
    ):
        logger.warning(
            "order_cancellation_rejected",
            extra=cls._build_payload(
                event="order_cancellation_rejected",
                order=order,
                performed_by=performed_by,
                reason=reason,
                metadata=metadata,
            ),
        )

    @classmethod
    def log_payment_status_updated(
        cls,
        *,
        order,
        previous_status=None,
        new_status=None,
        metadata=None,
    ):
        logger.info(
            "order_payment_status_updated",
            extra=cls._build_payload(
                event="order_payment_status_updated",
                order=order,
                metadata={
                    "previous_payment_status": previous_status,
                    "new_payment_status": new_status,
                    **(metadata or {}),
                },
            ),
        )

    @classmethod
    def _build_payload(
        cls,
        *,
        event,
        order=None,
        customer=None,
        performed_by=None,
        idempotency_key=None,
        reason=None,
        metadata=None,
    ):
        payload = {
            "event": event,
            "order_id": cls._extract_attr(order, "id"),
            "customer_id": (
                cls._extract_attr(order, "customer_id")
                if order is not None
                else cls._extract_attr(customer, "id")
            ),
            "performed_by_id": cls._extract_attr(performed_by, "id"),
            "status": cls._extract_attr(order, "status"),
            "payment_status": cls._extract_attr(order, "payment_status"),
            "shipping_status": cls._extract_attr(order, "shipping_status"),
            "idempotency_key": (
                cls._serialize(idempotency_key)
                if idempotency_key is not None
                else cls._extract_attr(order, "idempotency_key")
            ),
            "reason": cls._serialize(reason),
            "metadata": cls._serialize(metadata or {}),
        }

        return payload

    @staticmethod
    def _extract_attr(instance, attr_name):
        if instance is None:
            return None
        return OrderLogService._serialize(getattr(instance, attr_name, None))

    @classmethod
    def _serialize(cls, value):
        if value is None:
            return None

        if isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, Decimal):
            return str(value)

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, dict):
            return {
                str(key): cls._serialize(val)
                for key, val in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [cls._serialize(item) for item in value]

        return str(value)