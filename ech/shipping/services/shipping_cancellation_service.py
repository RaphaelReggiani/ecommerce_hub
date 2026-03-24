from django.db import transaction

from ech.shipping.constants.messages import (
    SHIPMENT_CANCELLATION_NOT_ALLOWED,
)
from ech.shipping.exceptions import (
    ShipmentAlreadyCancelledException,
    ShipmentAlreadyDeliveredException,
    ShipmentCancellationNotAllowedException,
)
from ech.shipping.models import Shipment
from ech.shipping.services.shipping_status_service import (
    ShippingStatusService,
)
from ech.shipping.services.shipping_log_service import (
    ShippingLogService,
)


class ShippingCancellationService:
    """
    Service responsible for shipment cancellation operations.
    """

    NON_CANCELLABLE_STATUSES = {
        Shipment.STATUS_DELIVERED,
        Shipment.STATUS_RETURNED,
    }

    @classmethod
    @transaction.atomic
    def cancel_shipment(
        cls,
        *,
        shipment,
        performed_by=None,
        metadata=None,
    ):
        """
        Cancel a shipment when business rules allow it.

        Args:
            shipment: Shipment instance.
            performed_by: Optional user performing the action.
            metadata: Optional metadata for audit/event trail.

        Returns:
            Shipment: Updated cancelled shipment instance.

        Raises:
            ShipmentAlreadyCancelledException:
                If the shipment is already cancelled.
            ShipmentAlreadyDeliveredException:
                If the shipment has already been delivered.
            ShipmentCancellationNotAllowedException:
                If cancellation is not allowed in the current state.
        """

        cls._validate_can_be_cancelled(shipment=shipment)

        cancellation_metadata = {
            "action": "shipment_cancelled",
            **(metadata or {}),
        }

        cancelled_shipment = ShippingStatusService.update_status(
            shipment=shipment,
            new_status=Shipment.STATUS_CANCELLED,
            performed_by=performed_by,
            metadata=cancellation_metadata,
        )

        ShippingLogService.log_shipment_cancelled(
            shipment=cancelled_shipment,
            performed_by=performed_by,
        )

        return cancelled_shipment
    
    @classmethod
    def _validate_can_be_cancelled(cls, *, shipment):
        """
        Validate whether the shipment can be cancelled.
        """

        if shipment.status == Shipment.STATUS_CANCELLED:
            raise ShipmentAlreadyCancelledException()

        if shipment.status == Shipment.STATUS_DELIVERED:
            raise ShipmentAlreadyDeliveredException()

        if shipment.status in cls.NON_CANCELLABLE_STATUSES:
            raise ShipmentCancellationNotAllowedException(
                SHIPMENT_CANCELLATION_NOT_ALLOWED
            )