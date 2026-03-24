import logging


logger = logging.getLogger(__name__)


class ShippingLogService:
    """
    Service responsible for structured shipping domain logs.
    """

    @staticmethod
    def log_shipment_created(*, shipment, performed_by=None):
        """
        Log shipment creation.
        """

        logger.info(
            "Shipment created.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "status": shipment.status,
                "shipping_method": shipment.shipping_method,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_shipment_updated(
        *,
        shipment,
        shipment_changed_fields=None,
        address_changed_fields=None,
        performed_by=None,
    ):
        """
        Log shipment update.
        """

        logger.info(
            "Shipment updated.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "status": shipment.status,
                "shipment_changed_fields": shipment_changed_fields or [],
                "address_changed_fields": address_changed_fields or [],
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_shipment_status_changed(
        *,
        shipment,
        previous_status,
        new_status,
        performed_by=None,
    ):
        """
        Log shipment status transition.
        """

        logger.info(
            "Shipment status changed.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "previous_status": previous_status,
                "new_status": new_status,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_shipment_cancelled(*, shipment, performed_by=None):
        """
        Log shipment cancellation.
        """

        logger.info(
            "Shipment cancelled.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "status": shipment.status,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_tracking_updated(
        *,
        shipment,
        tracking_update,
        performed_by=None,
    ):
        """
        Log shipment tracking update.
        """

        logger.info(
            "Shipment tracking updated.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "tracking_update_id": tracking_update.id,
                "tracking_status": tracking_update.status,
                "tracking_location": tracking_update.location,
                "tracking_event_at": tracking_update.event_at.isoformat(),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )