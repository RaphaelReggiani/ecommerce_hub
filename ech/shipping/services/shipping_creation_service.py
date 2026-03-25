from django.db import transaction

from ech.shipping.domain_events.dispatcher import DomainEventDispatcher
from ech.shipping.domain_events.events import ShipmentCreatedEvent
from ech.shipping.exceptions import (
    ShipmentAlreadyExistsException,
    InvalidShippingAddressException,
)
from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentEvent,
    ShipmentLifecycle,
)
from ech.shipping.services.shipping_log_service import ShippingLogService


class ShippingCreationService:
    """
    Service responsible for shipment creation.

    Creates the shipment aggregate root plus its initial related
    records such as address snapshot, lifecycle, and audit event.
    """

    @classmethod
    @transaction.atomic
    def create_shipment(
        cls,
        *,
        order,
        customer,
        shipping_method,
        address_data,
        shipping_cost=0,
        currency="USD",
        carrier_name="",
        tracking_code=None,
        external_reference=None,
        estimated_delivery_date=None,
        idempotency_key=None,
        performed_by=None,
    ):
        """
        Create a shipment for an order.

        Args:
            order: Related order instance.
            customer: Shipment customer instance.
            shipping_method: Shipping method choice value.
            address_data: Dictionary containing shipment address snapshot.
            shipping_cost: Decimal shipping cost.
            currency: Currency code.
            carrier_name: Optional carrier name.
            tracking_code: Optional shipment tracking code.
            external_reference: Optional external carrier reference.
            estimated_delivery_date: Optional expected delivery date.
            idempotency_key: Optional idempotency key.
            performed_by: Optional user performing the action.

        Returns:
            Shipment: Created shipment instance.

        Raises:
            ShipmentAlreadyExistsException:
                If a shipment already exists for the given order.
            InvalidShippingAddressException:
                If required address fields are missing.
        """

        cls._validate_shipment_does_not_exist(order=order)
        cls._validate_address_data(address_data=address_data)

        shipment = Shipment.objects.create(
            order=order,
            customer=customer,
            status=Shipment.STATUS_PENDING,
            shipping_method=shipping_method,
            carrier_name=carrier_name,
            tracking_code=tracking_code,
            external_reference=external_reference,
            idempotency_key=idempotency_key,
            shipping_cost=shipping_cost,
            currency=currency,
            estimated_delivery_date=estimated_delivery_date,
        )

        ShipmentAddress.objects.create(
            shipment=shipment,
            full_name=address_data["full_name"],
            address_line=address_data["address_line"],
            city=address_data["city"],
            state=address_data["state"],
            country=address_data["country"],
            postal_code=address_data["postal_code"],
            phone=address_data.get("phone", ""),
            delivery_instructions=address_data.get(
                "delivery_instructions", ""
            ),
        )

        ShipmentLifecycle.objects.create(
            shipment=shipment,
        )

        ShipmentEvent.objects.create(
            shipment=shipment,
            event_type=ShipmentEvent.TYPE_CREATED,
            performed_by=performed_by,
            metadata={
                "order_id": str(order.id),
                "customer_id": str(customer.id),
                "shipping_method": shipping_method,
                "tracking_code": tracking_code,
                "carrier_name": carrier_name,
                "estimated_delivery_date": (
                    estimated_delivery_date.isoformat()
                    if estimated_delivery_date
                    else None
                ),
            },
        )

        ShippingLogService.log_shipment_created(
            shipment=shipment,
            performed_by=performed_by,
        )

        DomainEventDispatcher.dispatch(
            ShipmentCreatedEvent(
                shipment_id=shipment.id,
                order_id=order.id,
                customer_id=customer.id,
                performed_by_id=getattr(performed_by, "id", None),
            )
        )

        return shipment

    @staticmethod
    def _validate_shipment_does_not_exist(*, order):
        """
        Ensure the order does not already have an associated shipment.
        """

        if Shipment.objects.filter(order=order).exists():
            raise ShipmentAlreadyExistsException()

    @staticmethod
    def _validate_address_data(*, address_data):
        """
        Validate required address snapshot fields.
        """

        required_fields = (
            "full_name",
            "address_line",
            "city",
            "state",
            "country",
            "postal_code",
        )

        missing_fields = [
            field for field in required_fields
            if not address_data.get(field)
        ]

        if missing_fields:
            raise InvalidShippingAddressException(
                f"Missing required shipping address fields: "
                f"{', '.join(missing_fields)}."
            )