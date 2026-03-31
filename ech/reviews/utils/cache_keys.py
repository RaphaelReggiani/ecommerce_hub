import hashlib
import json


def _normalize_value(value):
    """
    Normalize cache key values into JSON-serializable primitives.
    """
    if isinstance(value, dict):
        return {
            str(key): _normalize_value(val)
            for key, val in sorted(value.items(), key=lambda item: str(item[0]))
        }

    if isinstance(value, (list, tuple, set)):
        return [_normalize_value(item) for item in value]

    return str(value)


def _build_hash(payload):
    """
    Build a stable hash from arbitrary payload data.
    """
    normalized = _normalize_value(payload)
    serialized = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.md5(serialized.encode("utf-8")).hexdigest()


def build_review_detail_cache_key(*, prefix, review_id, version):
    """
    Build cache key for review detail retrieval.
    """
    return f"{prefix}:v{version}:review:{review_id}"


def build_customer_review_list_cache_key(
    *,
    prefix,
    customer_id,
    version,
    filters=None,
):
    """
    Build cache key for customer review list retrieval.
    """
    filters_hash = _build_hash(filters or {})
    return (
        f"{prefix}:v{version}:customer:{customer_id}:filters:{filters_hash}"
    )


def build_management_review_list_cache_key(
    *,
    prefix,
    version,
    filters=None,
):
    """
    Build cache key for management review list retrieval.
    """
    filters_hash = _build_hash(filters or {})
    return f"{prefix}:v{version}:filters:{filters_hash}"


def build_public_product_review_list_cache_key(
    *,
    prefix,
    product_id,
    version,
    filters=None,
):
    """
    Build cache key for public product review list retrieval.
    """
    filters_hash = _build_hash(filters or {})
    return f"{prefix}:v{version}:product:{product_id}:filters:{filters_hash}"


def build_product_review_summary_cache_key(
    *,
    prefix,
    product_id,
    version,
):
    """
    Build cache key for product review summary retrieval.
    """
    return f"{prefix}:v{version}:product:{product_id}:summary"


def build_namespace_version_cache_key(*, prefix, identifier=None):
    """
    Build cache key used to store namespace versions.

    Examples:
    - detail version per review
    - list version per customer
    - public product list version per product
    - summary version per product
    - global management list version
    """
    if identifier is None:
        return prefix

    return f"{prefix}:{identifier}"