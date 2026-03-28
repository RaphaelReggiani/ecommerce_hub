from django.db import transaction
from django.utils import timezone

from ech.shipping.domain_events.dispatcher import DomainEventDispatcher
from ech.shipping.domain_events.events import ShipmentStatusChangedEvent
from ech.shipping.exceptions import (
    InvalidShipmentStatusTransitionException,
    ShipmentAlreadyCancelledException,
    ShipmentAlreadyDeliveredException,
)
from ech.shipping.models import (
    Shipment,
    ShipmentEvent,
)
from ech.shipping.services.shipping_log_service import (
    ShippingLogService,
)

from ech.shipping.services.cache_service import (
    ShippingCacheService,
)


class ShippingStatusService:
    """
    Service responsible for shipment status transitions.
    """

    ALLOWED_TRANSITIONS = {
        Shipment.STATUS_PENDING: {
            Shipment.STATUS_PREPARING,
            Shipment.STATUS_CANCELLED,
        },
        Shipment.STATUS_PREPARING: {
            Shipment.STATUS_READY_TO_SHIP,
            Shipment.STATUS_CANCELLED,
        },
        Shipment.STATUS_READY_TO_SHIP: {
            Shipment.STATUS_SHIPPED,
            Shipment.STATUS_CANCELLED,
        },
        Shipment.STATUS_SHIPPED: {
            Shipment.STATUS_IN_TRANSIT,
            Shipment.STATUS_FAILED,
            Shipment.STATUS_RETURNED,
        },
        Shipment.STATUS_IN_TRANSIT: {
            Shipment.STATUS_OUT_FOR_DELIVERY,
            Shipment.STATUS_FAILED,
            Shipment.STATUS_RETURNED,
        },
        Shipment.STATUS_OUT_FOR_DELIVERY: {
            Shipment.STATUS_DELIVERED,
            Shipment.STATUS_FAILED,
            Shipment.STATUS_RETURNED,
        },
        Shipment.STATUS_FAILED: {
            Shipment.STATUS_RETURNED,
        },
        Shipment.STATUS_RETURNED: set(),
        Shipment.STATUS_DELIVERED: set(),
        Shipment.STATUS_CANCELLED: set(),
    }

    EVENT_TYPE_MAP = {
        Shipment.STATUS_PREPARING: ShipmentEvent.TYPE_PREPARING_STARTED,
        Shipment.STATUS_READY_TO_SHIP: ShipmentEvent.TYPE_READY_TO_SHIP,
        Shipment.STATUS_SHIPPED: ShipmentEvent.TYPE_SHIPPED,
        Shipment.STATUS_IN_TRANSIT: ShipmentEvent.TYPE_IN_TRANSIT,
        Shipment.STATUS_OUT_FOR_DELIVERY: ShipmentEvent.TYPE_OUT_FOR_DELIVERY,
        Shipment.STATUS_DELIVERED: ShipmentEvent.TYPE_DELIVERED,
        Shipment.STATUS_FAILED: ShipmentEvent.TYPE_FAILED,
        Shipment.STATUS_RETURNED: ShipmentEvent.TYPE_RETURNED,
        Shipment.STATUS_CANCELLED: ShipmentEvent.TYPE_CANCELLED,
    }

    LIFECYCLE_FIELD_MAP = {
        Shipment.STATUS_PREPARING: "preparing_at",
        Shipment.STATUS_READY_TO_SHIP: "ready_to_ship_at",
        Shipment.STATUS_SHIPPED: "shipped_at",
        Shipment.STATUS_IN_TRANSIT: "in_transit_at",
        Shipment.STATUS_OUT_FOR_DELIVERY: "out_for_delivery_at",
        Shipment.STATUS_DELIVERED: "delivered_at",
        Shipment.STATUS_FAILED: "failed_at",
        Shipment.STATUS_RETURNED: "returned_at",
        Shipment.STATUS_CANCELLED: "cancelled_at",
    }

    @classmethod
    @transaction.atomic
    def update_status(
        cls,
        *,
        shipment,
        new_status,
        performed_by=None,
        metadata=None,
    ):
        """
        Update shipment status in a controlled and auditable way.

        Args:
            shipment: Shipment instance.
            new_status: Target shipment status.
            performed_by: Optional user performing the action.
            metadata: Optional additional metadata for audit trail.

        Returns:
            Shipment: Updated shipment instance.

        Raises:
            ShipmentAlreadyDeliveredException:
                If shipment is already delivered.
            ShipmentAlreadyCancelledException:
                If shipment is already cancelled.
            InvalidShipmentStatusTransitionException:
                If transition is not allowed.
        """

        current_status = shipment.status

        cls._validate_terminal_status(shipment=shipment)
        cls._validate_transition(
            current_status=current_status,
            new_status=new_status,
        )

        shipment.status = new_status
        shipment.save(update_fields=["status", "updated_at"])

        cls._update_lifecycle_timestamp(
            shipment=shipment,
            new_status=new_status,
        )

        cls._create_status_change_event(
            shipment=shipment,
            previous_status=current_status,
            new_status=new_status,
            performed_by=performed_by,
            metadata=metadata,
        )

        ShippingLogService.log_shipment_status_changed(
            shipment=shipment,
            previous_status=current_status,
            new_status=new_status,
            performed_by=performed_by,
        )

        DomainEventDispatcher.dispatch(
            ShipmentStatusChangedEvent(
                shipment_id=shipment.id,
                previous_status=current_status,
                new_status=new_status,
                performed_by_id=getattr(performed_by, "id", None),
            )
        )

        transaction.on_commit(
            lambda: ShippingCacheService.invalidate_after_mutation(
                shipment_id=shipment.id,
                customer_id=shipment.customer_id,
                order_id=shipment.order_id,
            )
        )

        return shipment

    @classmethod
    def _validate_terminal_status(cls, *, shipment):
        """
        Prevent changes to terminal shipment states.
        """

        if shipment.status == Shipment.STATUS_DELIVERED:
            raise ShipmentAlreadyDeliveredException()

        if shipment.status == Shipment.STATUS_CANCELLED:
            raise ShipmentAlreadyCancelledException()

    @classmethod
    def _validate_transition(cls, *, current_status, new_status):
        """
        Validate whether the status transition is allowed.
        """

        allowed_statuses = cls.ALLOWED_TRANSITIONS.get(
            current_status,
            set(),
        )

        if new_status not in allowed_statuses:
            raise InvalidShipmentStatusTransitionException()

    @classmethod
    def _update_lifecycle_timestamp(cls, *, shipment, new_status):
        """
        Update the lifecycle timestamp associated with the new status.
        """

        lifecycle = shipment.lifecycle
        lifecycle_field = cls.LIFECYCLE_FIELD_MAP.get(new_status)

        if not lifecycle_field:
            return

        setattr(lifecycle, lifecycle_field, timezone.now())
        lifecycle.save(update_fields=[lifecycle_field, "updated_at"])

    @classmethod
    def _create_status_change_event(
        cls,
        *,
        shipment,
        previous_status,
        new_status,
        performed_by=None,
        metadata=None,
    ):
        """
        Create audit trail records for shipment status transition.
        """

        ShipmentEvent.objects.create(
            shipment=shipment,
            event_type=ShipmentEvent.TYPE_STATUS_CHANGED,
            performed_by=performed_by,
            metadata={
                "previous_status": previous_status,
                "new_status": new_status,
                **(metadata or {}),
            },
        )

        specific_event_type = cls.EVENT_TYPE_MAP.get(new_status)

        if specific_event_type:
            ShipmentEvent.objects.create(
                shipment=shipment,
                event_type=specific_event_type,
                performed_by=performed_by,
                metadata=metadata or {},
            )