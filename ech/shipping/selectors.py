from django.db.models import Q

from ech.shipping.models import Shipment
from ech.shipping.exceptions import (
    ShipmentAccessDeniedException,
    ShipmentNotFoundException,
)


def shipment_base_queryset():
    """
    Base optimized queryset for shipment retrieval.
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


def get_shipment_by_id(*, shipment_id):
    """
    Retrieve a shipment by its ID using the optimized base queryset.

    Args:
        shipment_id: Shipment UUID.

    Returns:
        Shipment: Matching shipment instance.

    Raises:
        ShipmentNotFoundException:
            If shipment does not exist.
    """

    shipment = shipment_base_queryset().filter(id=shipment_id).first()

    if not shipment:
        raise ShipmentNotFoundException()

    return shipment


def get_shipment_by_order_id(*, order_id):
    """
    Retrieve a shipment by its related order ID.

    Args:
        order_id: Order UUID or ID.

    Returns:
        Shipment: Matching shipment instance.

    Raises:
        ShipmentNotFoundException:
            If shipment does not exist for the given order.
    """

    shipment = shipment_base_queryset().filter(order_id=order_id).first()

    if not shipment:
        raise ShipmentNotFoundException()

    return shipment


def get_customer_shipment(*, shipment_id, customer):
    """
    Retrieve a shipment ensuring it belongs to the given customer.

    Args:
        shipment_id: Shipment UUID.
        customer: Authenticated customer user.

    Returns:
        Shipment: Matching shipment instance.

    Raises:
        ShipmentNotFoundException:
            If shipment does not exist.
        ShipmentAccessDeniedException:
            If shipment does not belong to the customer.
    """

    shipment = get_shipment_by_id(shipment_id=shipment_id)

    if shipment.customer_id != customer.id:
        raise ShipmentAccessDeniedException()

    return shipment


def list_customer_shipments(*, customer):
    """
    List shipments belonging to a specific customer.

    Args:
        customer: Authenticated customer user.

    Returns:
        QuerySet[Shipment]: Customer shipments queryset.
    """

    return shipment_base_queryset().filter(
        customer=customer
    ).order_by("-created_at")


def list_customer_shipments_by_status(*, customer, status_value):
    """
    List customer shipments filtered by status.

    Args:
        customer: Authenticated customer user.
        status_value: Shipment status value.

    Returns:
        QuerySet[Shipment]: Filtered customer shipments queryset.
    """

    return shipment_base_queryset().filter(
        customer=customer,
        status=status_value,
    ).order_by("-created_at")


def list_management_shipments():
    """
    List all shipments for management and staff operations.

    Returns:
        QuerySet[Shipment]: Management shipment queryset.
    """

    return shipment_base_queryset().order_by("-created_at")


def list_shipments_by_status(*, status_value):
    """
    List all shipments filtered by status for management use.

    Args:
        status_value: Shipment status value.

    Returns:
        QuerySet[Shipment]: Filtered shipment queryset.
    """

    return shipment_base_queryset().filter(
        status=status_value
    ).order_by("-created_at")


def list_shipments_by_shipping_method(*, shipping_method):
    """
    List all shipments filtered by shipping method.

    Args:
        shipping_method: Shipping method value.

    Returns:
        QuerySet[Shipment]: Filtered shipment queryset.
    """

    return shipment_base_queryset().filter(
        shipping_method=shipping_method
    ).order_by("-created_at")


def list_shipments_by_carrier(*, carrier_name):
    """
    List all shipments filtered by carrier name.

    Args:
        carrier_name: Carrier name string.

    Returns:
        QuerySet[Shipment]: Filtered shipment queryset.
    """

    return shipment_base_queryset().filter(
        carrier_name__iexact=carrier_name
    ).order_by("-created_at")


def list_shipments_due_for_delivery(*, delivery_date):
    """
    List shipments expected for a specific delivery date.

    Args:
        delivery_date: Date object.

    Returns:
        QuerySet[Shipment]: Shipments with matching estimated delivery date.
    """

    return shipment_base_queryset().filter(
        estimated_delivery_date=delivery_date
    ).order_by("-created_at")


def list_shipments_with_tracking_code():
    """
    List shipments that already have a tracking code assigned.

    Returns:
        QuerySet[Shipment]: Shipments with tracking code.
    """

    return shipment_base_queryset().exclude(
        tracking_code__isnull=True
    ).exclude(
        tracking_code=""
    ).order_by("-created_at")


def search_shipments(*, query):
    """
    Search shipments across tracking code, carrier, external reference,
    and order identifier fields.

    Args:
        query: Search string.

    Returns:
        QuerySet[Shipment]: Matching shipment queryset.
    """

    return shipment_base_queryset().filter(
        Q(tracking_code__icontains=query)
        | Q(carrier_name__icontains=query)
        | Q(external_reference__icontains=query)
    ).order_by("-created_at")