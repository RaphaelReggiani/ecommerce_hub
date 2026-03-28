from django.core.cache import cache

from ech.shipping.constants.cache import (
    SHIPPING_CACHE_DEFAULT_VERSION,
    SHIPPING_CACHE_TIMEOUT_DEFAULT,
)
from ech.shipping.utils.cache_keys import (
    customer_version_key,
    management_version_key,
    order_version_key,
    shipment_version_key,
)


class ShippingCacheService:
    """
    Service responsible for shipping cache operations and cache invalidation.
    """

    @staticmethod
    def get(*, key, default=None):
        return cache.get(key, default)

    @staticmethod
    def set(*, key, value, timeout=SHIPPING_CACHE_TIMEOUT_DEFAULT):
        cache.set(key, value, timeout)

    @staticmethod
    def delete(*, key):
        cache.delete(key)

    @classmethod
    def get_or_set(
        cls,
        *,
        key,
        producer,
        timeout=SHIPPING_CACHE_TIMEOUT_DEFAULT,
    ):
        cached_value = cls.get(key=key)

        if cached_value is not None:
            return cached_value

        value = producer()
        cls.set(
            key=key,
            value=value,
            timeout=timeout,
        )
        return value

    @classmethod
    def get_shipment_version(cls, *, shipment_id):
        key = shipment_version_key(shipment_id=shipment_id)
        return cls.get(key=key, default=SHIPPING_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_customer_version(cls, *, customer_id):
        key = customer_version_key(customer_id=customer_id)
        return cls.get(key=key, default=SHIPPING_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_order_version(cls, *, order_id):
        key = order_version_key(order_id=order_id)
        return cls.get(key=key, default=SHIPPING_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_management_version(cls):
        key = management_version_key()
        return cls.get(key=key, default=SHIPPING_CACHE_DEFAULT_VERSION)

    @classmethod
    def bump_shipment_version(cls, *, shipment_id):
        key = shipment_version_key(shipment_id=shipment_id)
        current = cls.get(key=key, default=SHIPPING_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_customer_version(cls, *, customer_id):
        key = customer_version_key(customer_id=customer_id)
        current = cls.get(key=key, default=SHIPPING_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_order_version(cls, *, order_id):
        key = order_version_key(order_id=order_id)
        current = cls.get(key=key, default=SHIPPING_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_management_version(cls):
        key = management_version_key()
        current = cls.get(key=key, default=SHIPPING_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def invalidate_after_mutation(
        cls,
        *,
        shipment_id,
        customer_id,
        order_id,
    ):
        """
        Invalidate all relevant cache namespaces after a shipment mutation.
        """
        cls.bump_shipment_version(shipment_id=shipment_id)
        cls.bump_customer_version(customer_id=customer_id)
        cls.bump_order_version(order_id=order_id)
        cls.bump_management_version()