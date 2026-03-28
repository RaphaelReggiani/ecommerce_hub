from ech.shipping.constants.cache import (
    SHIPPING_CACHE_CUSTOMER_PREFIX,
    SHIPPING_CACHE_DEFAULT_VERSION,
    SHIPPING_CACHE_DETAIL_PREFIX,
    SHIPPING_CACHE_MANAGEMENT_PREFIX,
    SHIPPING_CACHE_ORDER_LOOKUP_PREFIX,
    SHIPPING_CACHE_SEARCH_PREFIX,
    SHIPPING_CACHE_VERSION_PREFIX,
)


def _normalize_text(value):
    """
    Normalize text values for cache keys.
    """
    if value is None:
        return "none"

    return str(value).strip().lower().replace(" ", "_")


# =============================
# VERSION KEYS
# =============================

def shipment_version_key(*, shipment_id):
    return f"{SHIPPING_CACHE_VERSION_PREFIX}:shipment:{shipment_id}"


def customer_version_key(*, customer_id):
    return f"{SHIPPING_CACHE_VERSION_PREFIX}:customer:{customer_id}"


def order_version_key(*, order_id):
    return f"{SHIPPING_CACHE_VERSION_PREFIX}:order:{order_id}"


def management_version_key():
    return f"{SHIPPING_CACHE_VERSION_PREFIX}:management"


# =============================
# ENTITY KEYS
# =============================

def shipment_detail_cache_key(*, shipment_id, shipment_version):
    return (
        f"{SHIPPING_CACHE_DETAIL_PREFIX}:shipment:{shipment_id}:"
        f"v{shipment_version}"
    )


def shipment_by_order_cache_key(*, order_id, order_version):
    return (
        f"{SHIPPING_CACHE_ORDER_LOOKUP_PREFIX}:order:{order_id}:"
        f"v{order_version}"
    )


def customer_shipment_detail_cache_key(
    *,
    customer_id,
    shipment_id,
    customer_version,
    shipment_version,
):
    return (
        f"{SHIPPING_CACHE_CUSTOMER_PREFIX}:{customer_id}:shipment:{shipment_id}:"
        f"cv{customer_version}:sv{shipment_version}"
    )


# =============================
# CUSTOMER LIST KEYS
# =============================

def customer_shipment_list_cache_key(*, customer_id, customer_version):
    return (
        f"{SHIPPING_CACHE_CUSTOMER_PREFIX}:{customer_id}:list:"
        f"v{customer_version}"
    )


def customer_shipment_status_list_cache_key(
    *,
    customer_id,
    status,
    customer_version,
):
    return (
        f"{SHIPPING_CACHE_CUSTOMER_PREFIX}:{customer_id}:status:"
        f"{_normalize_text(status)}:v{customer_version}"
    )


# =============================
# MANAGEMENT LIST KEYS
# =============================

def management_shipment_list_cache_key(*, management_version):
    return f"{SHIPPING_CACHE_MANAGEMENT_PREFIX}:list:v{management_version}"


def management_shipment_status_cache_key(*, status, management_version):
    return (
        f"{SHIPPING_CACHE_MANAGEMENT_PREFIX}:status:"
        f"{_normalize_text(status)}:v{management_version}"
    )


def management_shipment_method_cache_key(
    *,
    shipping_method,
    management_version,
):
    return (
        f"{SHIPPING_CACHE_MANAGEMENT_PREFIX}:method:"
        f"{_normalize_text(shipping_method)}:v{management_version}"
    )


def management_shipment_carrier_cache_key(
    *,
    carrier_name,
    management_version,
):
    return (
        f"{SHIPPING_CACHE_MANAGEMENT_PREFIX}:carrier:"
        f"{_normalize_text(carrier_name)}:v{management_version}"
    )


def management_shipment_estimated_delivery_cache_key(
    *,
    estimated_delivery_date,
    management_version,
):
    return (
        f"{SHIPPING_CACHE_MANAGEMENT_PREFIX}:estimated-delivery:"
        f"{_normalize_text(estimated_delivery_date)}:v{management_version}"
    )


def management_shipment_tracking_presence_cache_key(*, management_version):
    return (
        f"{SHIPPING_CACHE_MANAGEMENT_PREFIX}:with-tracking:"
        f"v{management_version}"
    )


def shipment_search_cache_key(*, query, management_version):
    return (
        f"{SHIPPING_CACHE_SEARCH_PREFIX}:{_normalize_text(query)}:"
        f"v{management_version}"
    )