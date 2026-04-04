from django.core.cache import cache

from ech.notifications.constants.cache import (
    NOTIFICATION_CACHE_DEFAULT_VERSION,
    NOTIFICATION_CACHE_TIMEOUT_DEFAULT,
)
from ech.notifications.utils.cache_keys import (
    notification_version_key,
    recipient_version_key,
    management_version_key,
)


class NotificationCacheService:
    """
    Service responsible for notification cache operations and cache invalidation.
    """

    @staticmethod
    def get(*, key, default=None):
        return cache.get(key, default)

    @staticmethod
    def set(*, key, value, timeout=NOTIFICATION_CACHE_TIMEOUT_DEFAULT):
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
        timeout=NOTIFICATION_CACHE_TIMEOUT_DEFAULT,
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
    def get_notification_version(cls, *, notification_id):
        key = notification_version_key(notification_id=notification_id)
        return cls.get(
            key=key,
            default=NOTIFICATION_CACHE_DEFAULT_VERSION,
        )

    @classmethod
    def get_recipient_version(cls, *, recipient_id):
        key = recipient_version_key(recipient_id=recipient_id)
        return cls.get(
            key=key,
            default=NOTIFICATION_CACHE_DEFAULT_VERSION,
        )

    @classmethod
    def get_management_version(cls):
        key = management_version_key()
        return cls.get(
            key=key,
            default=NOTIFICATION_CACHE_DEFAULT_VERSION,
        )

    @classmethod
    def bump_notification_version(cls, *, notification_id):
        key = notification_version_key(notification_id=notification_id)

        current = cls.get(
            key=key,
            default=NOTIFICATION_CACHE_DEFAULT_VERSION,
        )

        cls.set(
            key=key,
            value=current + 1,
            timeout=None,
        )

    @classmethod
    def bump_recipient_version(cls, *, recipient_id):
        key = recipient_version_key(recipient_id=recipient_id)

        current = cls.get(
            key=key,
            default=NOTIFICATION_CACHE_DEFAULT_VERSION,
        )

        cls.set(
            key=key,
            value=current + 1,
            timeout=None,
        )

    @classmethod
    def bump_management_version(cls):
        key = management_version_key()

        current = cls.get(
            key=key,
            default=NOTIFICATION_CACHE_DEFAULT_VERSION,
        )

        cls.set(
            key=key,
            value=current + 1,
            timeout=None,
        )

    @classmethod
    def invalidate_after_mutation(
        cls,
        *,
        notification_id,
        recipient_id,
    ):
        """
        Invalidate all relevant cache namespaces after a notification mutation.

        This includes:
        - notification detail cache
        - recipient notification lists
        - management notification lists
        """

        cls.bump_notification_version(notification_id=notification_id)

        cls.bump_recipient_version(recipient_id=recipient_id)

        cls.bump_management_version()