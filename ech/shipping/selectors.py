from django.db.models import Q

from ech.shipping.constants.cache import (
    SHIPPING_CACHE_TIMEOUT_DEFAULT,
    SHIPPING_CACHE_TIMEOUT_LONG,
)
from ech.shipping.exceptions import (
    ShipmentAccessDeniedException,
    ShipmentNotFoundException,
)
from ech.shipping.models import Shipment
from ech.shipping.services.cache_service import ShippingCacheService
from ech.shipping.utils.cache_keys import (
    customer_shipment_detail_cache_key,
    customer_shipment_list_cache_key,
    customer_shipment_status_list_cache_key,
    management_shipment_carrier_cache_key,
    management_shipment_estimated_delivery_cache_key,
    management_shipment_list_cache_key,
    management_shipment_method_cache_key,
    management_shipment_status_cache_key,
    management_shipment_tracking_presence_cache_key,
    shipment_by_order_cache_key,
    shipment_detail_cache_key,
    shipment_search_cache_key,
)


def shipment_base_queryset():
    """
    Return the base shipment queryset with optimized related loading.
    """
    return Shipment.objects.select_related(
        "order",
        "customer",
        "address",
        "lifecycle",
    ).prefetch_related(
        "events",
        "tracking_updates",
        "notes",
    )


def _rebuild_queryset_from_ids(*, shipment_ids):
    """
    Rebuild queryset from cached shipment IDs.
    """
    return shipment_base_queryset().filter(id__in=shipment_ids)


def get_shipment_by_id(*, shipment_id):
    """
    Retrieve a shipment by ID with related objects.
    """
    shipment_version = ShippingCacheService.get_shipment_version(
        shipment_id=shipment_id
    )
    cache_key = shipment_detail_cache_key(
        shipment_id=shipment_id,
        shipment_version=shipment_version,
    )

    def producer():
        try:
            return shipment_base_queryset().get(id=shipment_id)
        except Shipment.DoesNotExist as exc:
            raise ShipmentNotFoundException() from exc

    return ShippingCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=SHIPPING_CACHE_TIMEOUT_DEFAULT,
    )


def get_shipment_with_related(*, shipment_id):
    """
    Retrieve a shipment by ID with related objects.
    Kept for compatibility with the original selector API.
    """
    return get_shipment_by_id(shipment_id=shipment_id)


def get_customer_shipment(*, customer, shipment_id):
    """
    Retrieve a shipment restricted to customer ownership.
    """
    shipment = get_shipment_by_id(shipment_id=shipment_id)

    if shipment.customer_id != customer.id:
        raise ShipmentAccessDeniedException()

    customer_version = ShippingCacheService.get_customer_version(
        customer_id=customer.id,
    )
    shipment_version = ShippingCacheService.get_shipment_version(
        shipment_id=shipment_id,
    )

    cache_key = customer_shipment_detail_cache_key(
        customer_id=customer.id,
        shipment_id=shipment_id,
        customer_version=customer_version,
        shipment_version=shipment_version,
    )

    def producer():
        return shipment

    return ShippingCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=SHIPPING_CACHE_TIMEOUT_DEFAULT,
    )


def get_shipment_by_order_id(*, order_id):
    """
    Retrieve a shipment by related order ID.
    """
    order_version = ShippingCacheService.get_order_version(order_id=order_id)
    cache_key = shipment_by_order_cache_key(
        order_id=order_id,
        order_version=order_version,
    )

    def producer():
        try:
            return shipment_base_queryset().get(order_id=order_id)
        except Shipment.DoesNotExist as exc:
            raise ShipmentNotFoundException() from exc

    return ShippingCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=SHIPPING_CACHE_TIMEOUT_DEFAULT,
    )


def list_customer_shipments(*, customer):
    """
    List shipments for a specific customer.
    """
    customer_version = ShippingCacheService.get_customer_version(
        customer_id=customer.id,
    )
    cache_key = customer_shipment_list_cache_key(
        customer_id=customer.id,
        customer_version=customer_version,
    )

    def producer():
        return list(
            shipment_base_queryset()
            .filter(customer=customer)
            .values_list("id", flat=True)
        )

    shipment_ids = ShippingCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=SHIPPING_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(shipment_ids=shipment_ids).filter(
        customer=customer
    )


def list_customer_shipments_by_status(*, customer, status):
    """
    List customer shipments filtered by status.
    """
    customer_version = ShippingCacheService.get_customer_version(
        customer_id=customer.id,
    )
    cache_key = customer_shipment_status_list_cache_key(
        customer_id=customer.id,
        status=status,
        customer_version=customer_version,
    )

    def producer():
        return list(
            shipment_base_queryset()
            .filter(customer=customer, status=status)
            .values_list("id", flat=True)
        )

    shipment_ids = ShippingCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=SHIPPING_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(shipment_ids=shipment_ids).filter(
        customer=customer,
        status=status,
    )


def list_shipments_by_status(*, status):
    """
    List shipments filtered by status.
    """
    management_version = ShippingCacheService.get_management_version()
    cache_key = management_shipment_status_cache_key(
        status=status,
        management_version=management_version,
    )

    def producer():
        return list(
            shipment_base_queryset()
            .filter(status=status)
            .values_list("id", flat=True)
        )

    shipment_ids = ShippingCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=SHIPPING_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(shipment_ids=shipment_ids).filter(
        status=status
    )


def list_shipments_by_shipping_method(*, shipping_method):
    """
    List shipments filtered by shipping method.
    """
    management_version = ShippingCacheService.get_management_version()
    cache_key = management_shipment_method_cache_key(
        shipping_method=shipping_method,
        management_version=management_version,
    )

    def producer():
        return list(
            shipment_base_queryset()
            .filter(shipping_method=shipping_method)
            .values_list("id", flat=True)
        )

    shipment_ids = ShippingCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=SHIPPING_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(shipment_ids=shipment_ids).filter(
        shipping_method=shipping_method
    )


def list_shipments_by_carrier(*, carrier_name):
    """
    List shipments filtered by carrier name.
    """
    management_version = ShippingCacheService.get_management_version()
    cache_key = management_shipment_carrier_cache_key(
        carrier_name=carrier_name,
        management_version=management_version,
    )

    def producer():
        return list(
            shipment_base_queryset()
            .filter(carrier_name__icontains=carrier_name)
            .values_list("id", flat=True)
        )

    shipment_ids = ShippingCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=SHIPPING_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(shipment_ids=shipment_ids).filter(
        carrier_name__icontains=carrier_name
    )


def list_recent_shipments():
    """
    List recent shipments.
    Kept compatible with the original selector API.
    """
    return shipment_base_queryset().order_by("-created_at")


def list_management_shipments():
    """
    List shipments for management dashboard.
    """
    management_version = ShippingCacheService.get_management_version()
    cache_key = management_shipment_list_cache_key(
        management_version=management_version,
    )

    def producer():
        return list(
            shipment_base_queryset()
            .values_list("id", flat=True)
        )

    shipment_ids = ShippingCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=SHIPPING_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(shipment_ids=shipment_ids)


def list_shipments_by_estimated_delivery_date(*, estimated_delivery_date):
    """
    List shipments filtered by estimated delivery date.
    """
    management_version = ShippingCacheService.get_management_version()
    cache_key = management_shipment_estimated_delivery_cache_key(
        estimated_delivery_date=estimated_delivery_date,
        management_version=management_version,
    )

    def producer():
        return list(
            shipment_base_queryset()
            .filter(estimated_delivery_date=estimated_delivery_date)
            .values_list("id", flat=True)
        )

    shipment_ids = ShippingCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=SHIPPING_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(shipment_ids=shipment_ids).filter(
        estimated_delivery_date=estimated_delivery_date
    )


def list_shipments_with_tracking():
    """
    List shipments that have tracking code.
    """
    management_version = ShippingCacheService.get_management_version()
    cache_key = management_shipment_tracking_presence_cache_key(
        management_version=management_version,
    )

    def producer():
        return list(
            shipment_base_queryset()
            .exclude(tracking_code__isnull=True)
            .exclude(tracking_code__exact="")
            .values_list("id", flat=True)
        )

    shipment_ids = ShippingCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=SHIPPING_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(shipment_ids=shipment_ids).exclude(
        tracking_code__isnull=True
    ).exclude(
        tracking_code__exact=""
    )


def search_shipments(*, query):
    """
    Search shipments by tracking code, carrier name, or external reference.
    """
    management_version = ShippingCacheService.get_management_version()
    cache_key = shipment_search_cache_key(
        query=query,
        management_version=management_version,
    )

    def producer():
        return list(
            shipment_base_queryset()
            .filter(
                Q(tracking_code__icontains=query)
                | Q(carrier_name__icontains=query)
                | Q(external_reference__icontains=query)
            )
            .values_list("id", flat=True)
        )

    shipment_ids = ShippingCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=SHIPPING_CACHE_TIMEOUT_DEFAULT,
    )

    return _rebuild_queryset_from_ids(shipment_ids=shipment_ids).filter(
        Q(tracking_code__icontains=query)
        | Q(carrier_name__icontains=query)
        | Q(external_reference__icontains=query)
    )