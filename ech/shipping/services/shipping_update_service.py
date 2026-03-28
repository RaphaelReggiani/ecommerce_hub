from django.db import transaction

from ech.shipping.constants.messages import (
    ADDRESS_UPDATE_NOT_ALLOWED,
    SHIPMENT_CANNOT_BE_MODIFIED,
)
from ech.shipping.exceptions import (
    InvalidShippingAddressException,
    ShipmentUpdateNotAllowedException,
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


class ShippingUpdateService:
    """
    Service responsible for updating editable shipment data.
    """

    NON_EDITABLE_STATUSES = {
        Shipment.STATUS_DELIVERED,
        Shipment.STATUS_CANCELLED,
        Shipment.STATUS_RETURNED,
    }

    ADDRESS_LOCKED_STATUSES = {
        Shipment.STATUS_PREPARING,
        Shipment.STATUS_READY_TO_SHIP,
        Shipment.STATUS_SHIPPED,
        Shipment.STATUS_IN_TRANSIT,
        Shipment.STATUS_OUT_FOR_DELIVERY,
        Shipment.STATUS_DELIVERED,
        Shipment.STATUS_FAILED,
        Shipment.STATUS_RETURNED,
        Shipment.STATUS_CANCELLED,
    }

    SHIPMENT_EDITABLE_FIELDS = {
        "shipping_method",
        "carrier_name",
        "tracking_code",
        "external_reference",
        "shipping_cost",
        "currency",
        "estimated_delivery_date",
        "delivered_to_name",
        "is_return_to_sender",
    }

    ADDRESS_EDITABLE_FIELDS = {
        "full_name",
        "address_line",
        "city",
        "state",
        "country",
        "postal_code",
        "phone",
        "delivery_instructions",
    }

    @classmethod
    @transaction.atomic
    def update_shipment(
        cls,
        *,
        shipment,
        shipment_data=None,
        address_data=None,
        performed_by=None,
        metadata=None,
    ):
        """
        Update editable shipment fields and, when allowed,
        its associated shipment address snapshot.

        Args:
            shipment: Shipment instance.
            shipment_data: Optional dict with shipment field updates.
            address_data: Optional dict with shipment address field updates.
            performed_by: Optional user performing the action.
            metadata: Optional metadata for audit trail.

        Returns:
            Shipment: Updated shipment instance.

        Raises:
            ShipmentUpdateNotAllowedException:
                If shipment cannot be modified in current state.
            InvalidShippingAddressException:
                If invalid address data is provided.
        """

        shipment_data = shipment_data or {}
        address_data = address_data or {}

        cls._validate_shipment_can_be_modified(shipment=shipment)

        shipment_changed_fields = cls._apply_shipment_updates(
            shipment=shipment,
            shipment_data=shipment_data,
        )

        address_changed_fields = cls._apply_address_updates(
            shipment=shipment,
            address_data=address_data,
        )

        if shipment_changed_fields:
            shipment.save(update_fields=shipment_changed_fields + ["updated_at"])

        if address_changed_fields:
            shipment.address.save(
                update_fields=address_changed_fields + ["updated_at"]
            )

        if shipment_changed_fields or address_changed_fields:
            cls._create_update_event(
                shipment=shipment,
                shipment_changed_fields=shipment_changed_fields,
                address_changed_fields=address_changed_fields,
                performed_by=performed_by,
                metadata=metadata,
            )

            ShippingLogService.log_shipment_updated(
                shipment=shipment,
                shipment_changed_fields=shipment_changed_fields,
                address_changed_fields=address_changed_fields,
                performed_by=performed_by,
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
    def _validate_shipment_can_be_modified(cls, *, shipment):
        """
        Validate whether shipment-level updates are allowed.
        """

        if shipment.status in cls.NON_EDITABLE_STATUSES:
            raise ShipmentUpdateNotAllowedException(
                SHIPMENT_CANNOT_BE_MODIFIED
            )

    @classmethod
    def _apply_shipment_updates(cls, *, shipment, shipment_data):
        """
        Apply allowed shipment field updates.

        Returns:
            list[str]: List of changed shipment fields.
        """

        changed_fields = []

        for field, value in shipment_data.items():
            if field not in cls.SHIPMENT_EDITABLE_FIELDS:
                continue

            if getattr(shipment, field) != value:
                setattr(shipment, field, value)
                changed_fields.append(field)

        return changed_fields

    @classmethod
    def _apply_address_updates(cls, *, shipment, address_data):
        """
        Apply allowed shipment address updates when permitted.

        Returns:
            list[str]: List of changed address fields.
        """

        if not address_data:
            return []

        cls._validate_address_can_be_updated(shipment=shipment)
        cls._validate_address_payload(address_data=address_data)

        address = shipment.address
        changed_fields = []

        for field, value in address_data.items():
            if field not in cls.ADDRESS_EDITABLE_FIELDS:
                continue

            if getattr(address, field) != value:
                setattr(address, field, value)
                changed_fields.append(field)

        return changed_fields

    @classmethod
    def _validate_address_can_be_updated(cls, *, shipment):
        """
        Validate whether shipment address can still be updated.
        """

        if shipment.status in cls.ADDRESS_LOCKED_STATUSES:
            raise ShipmentUpdateNotAllowedException(
                ADDRESS_UPDATE_NOT_ALLOWED
            )

    @staticmethod
    def _validate_address_payload(*, address_data):
        """
        Validate address payload consistency for required fields
        when those fields are explicitly provided.
        """

        required_fields = {
            "full_name",
            "address_line",
            "city",
            "state",
            "country",
            "postal_code",
        }

        invalid_required_fields = [
            field for field in address_data
            if field in required_fields and not address_data.get(field)
        ]

        if invalid_required_fields:
            raise InvalidShippingAddressException(
                "Invalid required address fields: "
                f"{', '.join(invalid_required_fields)}."
            )

    @staticmethod
    def _create_update_event(
        *,
        shipment,
        shipment_changed_fields,
        address_changed_fields,
        performed_by=None,
        metadata=None,
    ):
        """
        Create shipment update audit event.
        """

        ShipmentEvent.objects.create(
            shipment=shipment,
            event_type=ShipmentEvent.TYPE_UPDATED,
            performed_by=performed_by,
            metadata={
                "shipment_changed_fields": shipment_changed_fields,
                "address_changed_fields": address_changed_fields,
                **(metadata or {}),
            },
        )