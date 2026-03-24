from django.db import transaction

from ech.shipping.exceptions import (
    InvalidTrackingEventException,
)
from ech.shipping.models import (
    Shipment,
    ShipmentEvent,
    ShipmentTrackingUpdate,
)
from ech.shipping.services.shipping_log_service import (
    ShippingLogService,
)
from ech.shipping.services.shipping_status_service import (
    ShippingStatusService,
)


class ShippingTrackingService:
    """
    Service responsible for shipment tracking operations.
    """

    TRACKING_STATUS_MAP = {
        Shipment.STATUS_PREPARING: Shipment.STATUS_PREPARING,
        Shipment.STATUS_READY_TO_SHIP: Shipment.STATUS_READY_TO_SHIP,
        Shipment.STATUS_SHIPPED: Shipment.STATUS_SHIPPED,
        Shipment.STATUS_IN_TRANSIT: Shipment.STATUS_IN_TRANSIT,
        Shipment.STATUS_OUT_FOR_DELIVERY: Shipment.STATUS_OUT_FOR_DELIVERY,
        Shipment.STATUS_DELIVERED: Shipment.STATUS_DELIVERED,
        Shipment.STATUS_FAILED: Shipment.STATUS_FAILED,
        Shipment.STATUS_RETURNED: Shipment.STATUS_RETURNED,
    }

    @classmethod
    @transaction.atomic
    def register_tracking_update(
        cls,
        *,
        shipment,
        description,
        event_at,
        status=None,
        location="",
        raw_payload=None,
        tracking_code=None,
        carrier_name="",
        external_reference=None,
        performed_by=None,
    ):
        """
        Register a new tracking update for a shipment.

        Args:
            shipment: Shipment instance.
            description: Human-readable tracking description.
            event_at: Datetime when the tracking event happened.
            status: Optional shipment status represented by the tracking event.
            location: Optional location information.
            raw_payload: Optional original external payload.
            tracking_code: Optional tracking code to persist on shipment.
            carrier_name: Optional carrier name to persist on shipment.
            external_reference: Optional external shipment reference.
            performed_by: Optional user performing the action.

        Returns:
            ShipmentTrackingUpdate: Created tracking update instance.

        Raises:
            InvalidTrackingEventException:
                If required tracking data is invalid.
        """

        cls._validate_tracking_data(
            description=description,
            event_at=event_at,
            status=status,
        )

        shipment_changed = cls._update_shipment_tracking_metadata(
            shipment=shipment,
            tracking_code=tracking_code,
            carrier_name=carrier_name,
            external_reference=external_reference,
        )

        tracking_update = ShipmentTrackingUpdate.objects.create(
            shipment=shipment,
            status=status or "",
            location=location,
            description=description,
            raw_payload=raw_payload,
            event_at=event_at,
        )

        ShipmentEvent.objects.create(
            shipment=shipment,
            event_type=ShipmentEvent.TYPE_TRACKING_UPDATED,
            performed_by=performed_by,
            metadata={
                "tracking_update_id": tracking_update.id,
                "status": status,
                "location": location,
                "description": description,
                "event_at": event_at.isoformat(),
                "tracking_code": shipment.tracking_code,
                "carrier_name": shipment.carrier_name,
                "external_reference": shipment.external_reference,
            },
        )

        if shipment_changed:
            shipment.save(
                update_fields=[
                    "tracking_code",
                    "carrier_name",
                    "external_reference",
                    "updated_at",
                ]
            )

        if status and status != shipment.status:
            ShippingStatusService.update_status(
                shipment=shipment,
                new_status=status,
                performed_by=performed_by,
                metadata={
                    "source": "tracking_update",
                    "tracking_update_id": tracking_update.id,
                    "tracking_description": description,
                },
            )

        ShippingLogService.log_tracking_updated(
            shipment=shipment,
            tracking_update=tracking_update,
            performed_by=performed_by,
        )

        return tracking_update

    @classmethod
    def _validate_tracking_data(
        cls,
        *,
        description,
        event_at,
        status=None,
    ):
        """
        Validate required tracking update input data.
        """

        if not description:
            raise InvalidTrackingEventException(
                "Tracking description is required."
            )

        if not event_at:
            raise InvalidTrackingEventException(
                "Tracking event timestamp is required."
            )

        if status and status not in cls.TRACKING_STATUS_MAP:
            raise InvalidTrackingEventException()

    @staticmethod
    def _update_shipment_tracking_metadata(
        *,
        shipment,
        tracking_code=None,
        carrier_name="",
        external_reference=None,
    ):
        """
        Update shipment-level tracking metadata when new values are provided.

        Returns:
            bool: Whether shipment metadata changed.
        """

        changed = False

        if tracking_code and shipment.tracking_code != tracking_code:
            shipment.tracking_code = tracking_code
            changed = True

        if carrier_name and shipment.carrier_name != carrier_name:
            shipment.carrier_name = carrier_name
            changed = True

        if (
            external_reference
            and shipment.external_reference != external_reference
        ):
            shipment.external_reference = external_reference
            changed = True

        return changed