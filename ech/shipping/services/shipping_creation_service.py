from decimal import Decimal

from django.db import IntegrityError, transaction

from ech.shipping.domain_events.dispatcher import DomainEventDispatcher
from ech.shipping.domain_events.events import ShipmentCreatedEvent
from ech.shipping.exceptions import (
    IdempotencyConflictException,
    InvalidShippingAddressException,
    ShipmentAlreadyExistsException,
)
from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentEvent,
    ShipmentLifecycle,
)
from ech.shipping.services.shipping_log_service import (
    ShippingLogService,
)
from ech.shipping.services.cache_service import (
    ShippingCacheService,
)


class ShippingCreationService:
    """
    Service responsible for shipment creation.

    Creates the shipment aggregate root plus its initial related
    records such as address snapshot, lifecycle, and audit event.

    Idempotency behavior:
    - If the same idempotency_key is reused with the same logical payload,
      the existing shipment is returned.
    - If the same idempotency_key is reused with a different payload,
      an IdempotencyConflictException is raised.
    - If a shipment already exists for the order and no matching
      idempotency_key result can be reused, a ShipmentAlreadyExistsException
      is raised.
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
            Shipment: Created shipment instance, or the existing one if the
            same idempotency key is replayed with an equivalent payload.

        Raises:
            ShipmentAlreadyExistsException:
                If a shipment already exists for the given order.
            InvalidShippingAddressException:
                If required address fields are missing.
            IdempotencyConflictException:
                If the same idempotency key is reused with a different payload.
        """

        cls._validate_address_data(address_data=address_data)

        normalized_address_data = cls._normalized_address_data(
            address_data=address_data
        )
        normalized_shipping_cost = cls._normalized_decimal(shipping_cost)

        if idempotency_key:
            existing_shipment = cls._get_shipment_by_idempotency_key(
                idempotency_key=idempotency_key
            )
            if existing_shipment:
                cls._validate_idempotent_reuse(
                    shipment=existing_shipment,
                    order=order,
                    customer=customer,
                    shipping_method=shipping_method,
                    address_data=normalized_address_data,
                    shipping_cost=normalized_shipping_cost,
                    currency=currency,
                    carrier_name=carrier_name,
                    tracking_code=tracking_code,
                    external_reference=external_reference,
                    estimated_delivery_date=estimated_delivery_date,
                )
                return existing_shipment

        locked_order = cls._lock_order(order=order)
        cls._validate_shipment_does_not_exist(order=locked_order)

        try:
            shipment = Shipment.objects.create(
                order=locked_order,
                customer=customer,
                status=Shipment.STATUS_PENDING,
                shipping_method=shipping_method,
                carrier_name=carrier_name,
                tracking_code=tracking_code,
                external_reference=external_reference,
                idempotency_key=idempotency_key,
                shipping_cost=normalized_shipping_cost,
                currency=currency,
                estimated_delivery_date=estimated_delivery_date,
            )

            ShipmentAddress.objects.create(
                shipment=shipment,
                full_name=normalized_address_data["full_name"],
                address_line=normalized_address_data["address_line"],
                city=normalized_address_data["city"],
                state=normalized_address_data["state"],
                country=normalized_address_data["country"],
                postal_code=normalized_address_data["postal_code"],
                phone=normalized_address_data.get("phone", ""),
                delivery_instructions=normalized_address_data.get(
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
                    "order_id": str(locked_order.id),
                    "customer_id": str(customer.id),
                    "shipping_method": shipping_method,
                    "tracking_code": tracking_code,
                    "carrier_name": carrier_name,
                    "estimated_delivery_date": (
                        estimated_delivery_date.isoformat()
                        if estimated_delivery_date
                        else None
                    ),
                    "idempotency_key": (
                        str(idempotency_key) if idempotency_key else None
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
                    order_id=locked_order.id,
                    customer_id=customer.id,
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

        except IntegrityError as exc:
            resolved_shipment = cls._resolve_integrity_conflict(
                order=locked_order,
                customer=customer,
                shipping_method=shipping_method,
                address_data=normalized_address_data,
                shipping_cost=normalized_shipping_cost,
                currency=currency,
                carrier_name=carrier_name,
                tracking_code=tracking_code,
                external_reference=external_reference,
                estimated_delivery_date=estimated_delivery_date,
                idempotency_key=idempotency_key,
            )

            if resolved_shipment:
                return resolved_shipment

            raise exc

    @staticmethod
    def _lock_order(*, order):
        """
        Acquire a database lock on the related order row to serialize
        shipment creation attempts for the same order.
        """
        return order.__class__.objects.select_for_update().get(pk=order.pk)

    @staticmethod
    def _get_shipment_by_idempotency_key(*, idempotency_key):
        """
        Retrieve an existing shipment by idempotency key.
        """
        return (
            Shipment.objects.select_related(
                "order",
                "customer",
                "address",
                "lifecycle",
            )
            .filter(idempotency_key=idempotency_key)
            .first()
        )

    @classmethod
    def _resolve_integrity_conflict(
        cls,
        *,
        order,
        customer,
        shipping_method,
        address_data,
        shipping_cost,
        currency,
        carrier_name,
        tracking_code,
        external_reference,
        estimated_delivery_date,
        idempotency_key,
    ):
        """
        Resolve conflicts raised during concurrent creation attempts.

        Returns:
            Shipment | None: Existing shipment to reuse, if resolvable.

        Raises:
            ShipmentAlreadyExistsException:
                If a shipment already exists for the order.
            IdempotencyConflictException:
                If the idempotency key was reused with different payload.
        """
        if idempotency_key:
            existing_shipment = cls._get_shipment_by_idempotency_key(
                idempotency_key=idempotency_key
            )
            if existing_shipment:
                cls._validate_idempotent_reuse(
                    shipment=existing_shipment,
                    order=order,
                    customer=customer,
                    shipping_method=shipping_method,
                    address_data=address_data,
                    shipping_cost=shipping_cost,
                    currency=currency,
                    carrier_name=carrier_name,
                    tracking_code=tracking_code,
                    external_reference=external_reference,
                    estimated_delivery_date=estimated_delivery_date,
                )
                return existing_shipment

        if Shipment.objects.filter(order=order).exists():
            raise ShipmentAlreadyExistsException()

        return None

    @classmethod
    def _validate_idempotent_reuse(
        cls,
        *,
        shipment,
        order,
        customer,
        shipping_method,
        address_data,
        shipping_cost,
        currency,
        carrier_name,
        tracking_code,
        external_reference,
        estimated_delivery_date,
    ):
        """
        Ensure an existing shipment associated with the same idempotency key
        represents the same logical create request.
        """
        shipment_address = shipment.address

        same_payload = all(
            [
                shipment.order_id == order.id,
                shipment.customer_id == customer.id,
                shipment.shipping_method == shipping_method,
                cls._normalized_decimal(shipment.shipping_cost)
                == cls._normalized_decimal(shipping_cost),
                shipment.currency == currency,
                (shipment.carrier_name or "") == (carrier_name or ""),
                shipment.tracking_code == tracking_code,
                shipment.external_reference == external_reference,
                shipment.estimated_delivery_date == estimated_delivery_date,
                shipment_address.full_name == address_data["full_name"],
                shipment_address.address_line == address_data["address_line"],
                shipment_address.city == address_data["city"],
                shipment_address.state == address_data["state"],
                shipment_address.country == address_data["country"],
                shipment_address.postal_code == address_data["postal_code"],
                (shipment_address.phone or "")
                == address_data.get("phone", ""),
                (shipment_address.delivery_instructions or "")
                == address_data.get("delivery_instructions", ""),
            ]
        )

        if not same_payload:
            raise IdempotencyConflictException()

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

    @staticmethod
    def _normalized_address_data(*, address_data):
        """
        Normalize optional address values for stable idempotency comparison.
        """
        return {
            "full_name": address_data["full_name"],
            "address_line": address_data["address_line"],
            "city": address_data["city"],
            "state": address_data["state"],
            "country": address_data["country"],
            "postal_code": address_data["postal_code"],
            "phone": address_data.get("phone", "") or "",
            "delivery_instructions": (
                address_data.get("delivery_instructions", "") or ""
            ),
        }

    @staticmethod
    def _normalized_decimal(value):
        """
        Normalize decimal-like values for safe equality comparisons.
        """
        return Decimal(str(value))