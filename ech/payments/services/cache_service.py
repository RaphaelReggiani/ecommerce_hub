from django.core.cache import cache

from ech.payments.constants.cache import (
    CUSTOMER_PAYMENT_LIST_CACHE_TTL,
    MANAGEMENT_PAYMENT_LIST_CACHE_TTL,
    PAYMENT_DETAIL_CACHE_TTL,
    PAYMENT_METHOD_LIST_CACHE_TTL,
    PAYMENT_REFERENCE_CACHE_TTL,
    PAYMENT_REFUNDS_CACHE_TTL,
    PAYMENT_STATUS_LIST_CACHE_TTL,
    PAYMENT_TRANSACTIONS_CACHE_TTL,
    PAYMENTS_CACHE_VERSION,
)
from ech.payments.utils.cache_keys import PaymentCacheKeys


class PaymentCacheService:
    """
    Centralized cache service for payments domain.

    Responsibilities:
        - build versioned cache keys
        - get/set/delete cached values
        - provide domain-specific cache helpers
        - invalidate payment-related cache consistently
    """

    VERSION = PAYMENTS_CACHE_VERSION

    @classmethod
    def _build_key(cls, raw_key: str) -> str:
        """
        Build a versioned cache key.
        """

        return f"{cls.VERSION}:{raw_key}"

    @classmethod
    def get(cls, raw_key: str):
        """
        Return cached value for the given raw key.
        """

        return cache.get(cls._build_key(raw_key))

    @classmethod
    def set(cls, raw_key: str, value, timeout: int) -> None:
        """
        Store a value in cache using the given raw key and timeout.
        """

        cache.set(cls._build_key(raw_key), value, timeout)

    @classmethod
    def delete(cls, raw_key: str) -> None:
        """
        Remove a cached value by raw key.
        """

        cache.delete(cls._build_key(raw_key))

    @classmethod
    def get_or_set(cls, raw_key: str, factory, timeout: int):
        """
        Return cached value if present, otherwise evaluate factory(),
        cache the result, and return it.
        """

        full_key = cls._build_key(raw_key)
        cached_value = cache.get(full_key)

        if cached_value is not None:
            return cached_value

        value = factory()
        cache.set(full_key, value, timeout)
        return value

    @classmethod
    def get_payment_detail(cls, payment_id):
        key = PaymentCacheKeys.payment_detail(payment_id)
        return cls.get(key)

    @classmethod
    def set_payment_detail(cls, payment_id, value) -> None:
        key = PaymentCacheKeys.payment_detail(payment_id)
        cls.set(key, value, PAYMENT_DETAIL_CACHE_TTL)

    @classmethod
    def get_or_set_payment_detail(cls, payment_id, factory):
        key = PaymentCacheKeys.payment_detail(payment_id)
        return cls.get_or_set(key, factory, PAYMENT_DETAIL_CACHE_TTL)

    @classmethod
    def delete_payment_detail(cls, payment_id) -> None:
        key = PaymentCacheKeys.payment_detail(payment_id)
        cls.delete(key)

    @classmethod
    def get_payment_by_reference(cls, payment_reference: str):
        key = PaymentCacheKeys.payment_by_reference(payment_reference)
        return cls.get(key)

    @classmethod
    def set_payment_by_reference(cls, payment_reference: str, value) -> None:
        key = PaymentCacheKeys.payment_by_reference(payment_reference)
        cls.set(key, value, PAYMENT_REFERENCE_CACHE_TTL)

    @classmethod
    def get_or_set_payment_by_reference(cls, payment_reference: str, factory):
        key = PaymentCacheKeys.payment_by_reference(payment_reference)
        return cls.get_or_set(key, factory, PAYMENT_REFERENCE_CACHE_TTL)

    @classmethod
    def delete_payment_by_reference(cls, payment_reference: str) -> None:
        key = PaymentCacheKeys.payment_by_reference(payment_reference)
        cls.delete(key)

    @classmethod
    def get_customer_payments(cls, customer_id, page: int = 1):
        key = PaymentCacheKeys.customer_payments(customer_id, page)
        return cls.get(key)

    @classmethod
    def set_customer_payments(cls, customer_id, page: int, value) -> None:
        key = PaymentCacheKeys.customer_payments(customer_id, page)
        cls.set(key, value, CUSTOMER_PAYMENT_LIST_CACHE_TTL)

    @classmethod
    def get_or_set_customer_payments(cls, customer_id, page: int, factory):
        key = PaymentCacheKeys.customer_payments(customer_id, page)
        return cls.get_or_set(key, factory, CUSTOMER_PAYMENT_LIST_CACHE_TTL)

    @classmethod
    def delete_customer_payments(cls, customer_id, page: int = 1) -> None:
        key = PaymentCacheKeys.customer_payments(customer_id, page)
        cls.delete(key)

    @classmethod
    def get_management_payments(cls, page: int = 1):
        key = PaymentCacheKeys.management_payments(page)
        return cls.get(key)

    @classmethod
    def set_management_payments(cls, page: int, value) -> None:
        key = PaymentCacheKeys.management_payments(page)
        cls.set(key, value, MANAGEMENT_PAYMENT_LIST_CACHE_TTL)

    @classmethod
    def get_or_set_management_payments(cls, page: int, factory):
        key = PaymentCacheKeys.management_payments(page)
        return cls.get_or_set(key, factory, MANAGEMENT_PAYMENT_LIST_CACHE_TTL)

    @classmethod
    def delete_management_payments(cls, page: int = 1) -> None:
        key = PaymentCacheKeys.management_payments(page)
        cls.delete(key)

    @classmethod
    def get_payments_by_status(cls, status: str, page: int = 1):
        key = PaymentCacheKeys.payments_by_status(status, page)
        return cls.get(key)

    @classmethod
    def set_payments_by_status(cls, status: str, page: int, value) -> None:
        key = PaymentCacheKeys.payments_by_status(status, page)
        cls.set(key, value, PAYMENT_STATUS_LIST_CACHE_TTL)

    @classmethod
    def get_or_set_payments_by_status(cls, status: str, page: int, factory):
        key = PaymentCacheKeys.payments_by_status(status, page)
        return cls.get_or_set(key, factory, PAYMENT_STATUS_LIST_CACHE_TTL)

    @classmethod
    def delete_payments_by_status(cls, status: str, page: int = 1) -> None:
        key = PaymentCacheKeys.payments_by_status(status, page)
        cls.delete(key)

    @classmethod
    def get_payments_by_method(cls, method: str, page: int = 1):
        key = PaymentCacheKeys.payments_by_method(method, page)
        return cls.get(key)

    @classmethod
    def set_payments_by_method(cls, method: str, page: int, value) -> None:
        key = PaymentCacheKeys.payments_by_method(method, page)
        cls.set(key, value, PAYMENT_METHOD_LIST_CACHE_TTL)

    @classmethod
    def get_or_set_payments_by_method(cls, method: str, page: int, factory):
        key = PaymentCacheKeys.payments_by_method(method, page)
        return cls.get_or_set(key, factory, PAYMENT_METHOD_LIST_CACHE_TTL)

    @classmethod
    def delete_payments_by_method(cls, method: str, page: int = 1) -> None:
        key = PaymentCacheKeys.payments_by_method(method, page)
        cls.delete(key)

    @classmethod
    def get_payment_transactions(cls, payment_id):
        key = PaymentCacheKeys.payment_transactions(payment_id)
        return cls.get(key)

    @classmethod
    def set_payment_transactions(cls, payment_id, value) -> None:
        key = PaymentCacheKeys.payment_transactions(payment_id)
        cls.set(key, value, PAYMENT_TRANSACTIONS_CACHE_TTL)

    @classmethod
    def get_or_set_payment_transactions(cls, payment_id, factory):
        key = PaymentCacheKeys.payment_transactions(payment_id)
        return cls.get_or_set(key, factory, PAYMENT_TRANSACTIONS_CACHE_TTL)

    @classmethod
    def delete_payment_transactions(cls, payment_id) -> None:
        key = PaymentCacheKeys.payment_transactions(payment_id)
        cls.delete(key)

    @classmethod
    def get_payment_refunds(cls, payment_id):
        key = PaymentCacheKeys.payment_refunds(payment_id)
        return cls.get(key)

    @classmethod
    def set_payment_refunds(cls, payment_id, value) -> None:
        key = PaymentCacheKeys.payment_refunds(payment_id)
        cls.set(key, value, PAYMENT_REFUNDS_CACHE_TTL)

    @classmethod
    def get_or_set_payment_refunds(cls, payment_id, factory):
        key = PaymentCacheKeys.payment_refunds(payment_id)
        return cls.get_or_set(key, factory, PAYMENT_REFUNDS_CACHE_TTL)

    @classmethod
    def delete_payment_refunds(cls, payment_id) -> None:
        key = PaymentCacheKeys.payment_refunds(payment_id)
        cls.delete(key)

    @classmethod
    def invalidate_payment_detail_cache(
        cls,
        *,
        payment_id,
        payment_reference: str | None = None,
    ) -> None:
        """
        Invalidate direct payment detail cache.
        """

        cls.delete_payment_detail(payment_id)

        if payment_reference:
            cls.delete_payment_by_reference(payment_reference)

        cls.delete_payment_transactions(payment_id)
        cls.delete_payment_refunds(payment_id)

    @classmethod
    def invalidate_customer_payment_cache(
        cls,
        *,
        customer_id,
        page: int = 1,
    ) -> None:
        """
        Invalidate customer payment list cache.
        """

        cls.delete_customer_payments(customer_id, page)

    @classmethod
    def invalidate_management_payment_cache(
        cls,
        *,
        page: int = 1,
    ) -> None:
        """
        Invalidate management payment list cache.
        """

        cls.delete_management_payments(page)

    @classmethod
    def invalidate_filtered_payment_cache(
        cls,
        *,
        status: str | None = None,
        method: str | None = None,
        page: int = 1,
    ) -> None:
        """
        Invalidate filtered payment list caches when filter values are known.
        """

        if status:
            cls.delete_payments_by_status(status, page)

        if method:
            cls.delete_payments_by_method(method, page)

    @classmethod
    def invalidate_payment_related_cache(
        cls,
        *,
        payment_id,
        customer_id=None,
        payment_reference: str | None = None,
        status: str | None = None,
        method: str | None = None,
        page: int = 1,
    ) -> None:
        """
        Invalidate the most common payment-related cache entries.

        This should be the main entrypoint used by services after:
            - payment creation
            - payment processing
            - payment cancellation
            - refund request / processing / failure / cancellation
        """

        cls.invalidate_payment_detail_cache(
            payment_id=payment_id,
            payment_reference=payment_reference,
        )

        if customer_id is not None:
            cls.invalidate_customer_payment_cache(
                customer_id=customer_id,
                page=page,
            )

        cls.invalidate_management_payment_cache(page=page)

        cls.invalidate_filtered_payment_cache(
            status=status,
            method=method,
            page=page,
        )