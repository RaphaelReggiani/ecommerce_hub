from django.db.models import Q

from ech.notifications.constants.cache import (
    NOTIFICATION_CACHE_TIMEOUT_DEFAULT,
    NOTIFICATION_CACHE_TIMEOUT_LONG,
)
from ech.notifications.exceptions import (
    NotificationAccessDeniedException,
    NotificationNotFoundException,
)
from ech.notifications.models import Notification
from ech.notifications.services.cache_service import NotificationCacheService
from ech.notifications.utils.cache_keys import (
    management_notification_channel_cache_key,
    management_notification_detail_cache_key,
    management_notification_list_cache_key,
    management_notification_priority_cache_key,
    management_notification_status_cache_key,
    notification_detail_cache_key,
    notification_search_cache_key,
    recipient_notification_archived_list_cache_key,
    recipient_notification_detail_cache_key,
    recipient_notification_list_cache_key,
    recipient_notification_status_list_cache_key,
    recipient_notification_type_list_cache_key,
    recipient_notification_unread_list_cache_key,
)


def notification_base_queryset():
    """
    Return the base notification queryset with optimized related loading.
    """
    return Notification.objects.select_related(
        "recipient",
        "created_by",
        "lifecycle",
    ).prefetch_related(
        "deliveries",
        "events",
    )


def _rebuild_queryset_from_ids(*, notification_ids):
    """
    Rebuild queryset from cached notification IDs.
    """
    return notification_base_queryset().filter(id__in=notification_ids)


def get_notification_by_id(*, notification_id):
    """
    Retrieve a notification by ID with related objects.
    """
    notification_version = NotificationCacheService.get_notification_version(
        notification_id=notification_id,
    )
    cache_key = notification_detail_cache_key(
        notification_id=notification_id,
        notification_version=notification_version,
    )

    def producer():
        try:
            return notification_base_queryset().get(id=notification_id)
        except Notification.DoesNotExist as exc:
            raise NotificationNotFoundException() from exc

    return NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_DEFAULT,
    )


def get_notification_with_related(*, notification_id):
    """
    Retrieve a notification by ID with related objects.
    Kept for compatibility with the original selector API.
    """
    return get_notification_by_id(notification_id=notification_id)


def get_recipient_notification(*, recipient, notification_id):
    """
    Retrieve a notification restricted to recipient ownership.
    """
    notification = get_notification_by_id(notification_id=notification_id)

    if notification.recipient_id != recipient.id:
        raise NotificationAccessDeniedException()

    recipient_version = NotificationCacheService.get_recipient_version(
        recipient_id=recipient.id,
    )
    notification_version = NotificationCacheService.get_notification_version(
        notification_id=notification_id,
    )

    cache_key = recipient_notification_detail_cache_key(
        recipient_id=recipient.id,
        notification_id=notification_id,
        recipient_version=recipient_version,
        notification_version=notification_version,
    )

    def producer():
        return notification

    return NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_DEFAULT,
    )


def list_recipient_notifications(*, recipient):
    """
    List notifications for a specific recipient.
    """
    recipient_version = NotificationCacheService.get_recipient_version(
        recipient_id=recipient.id,
    )
    cache_key = recipient_notification_list_cache_key(
        recipient_id=recipient.id,
        recipient_version=recipient_version,
    )

    def producer():
        return list(
            notification_base_queryset()
            .filter(recipient=recipient)
            .values_list("id", flat=True)
        )

    notification_ids = NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(
        notification_ids=notification_ids,
    ).filter(
        recipient=recipient,
    )


def list_recipient_notifications_by_status(*, recipient, status):
    """
    List recipient notifications filtered by status.
    """
    recipient_version = NotificationCacheService.get_recipient_version(
        recipient_id=recipient.id,
    )
    cache_key = recipient_notification_status_list_cache_key(
        recipient_id=recipient.id,
        status=status,
        recipient_version=recipient_version,
    )

    def producer():
        return list(
            notification_base_queryset()
            .filter(recipient=recipient, status=status)
            .values_list("id", flat=True)
        )

    notification_ids = NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(
        notification_ids=notification_ids,
    ).filter(
        recipient=recipient,
        status=status,
    )


def list_recipient_notifications_by_type(*, recipient, notification_type):
    """
    List recipient notifications filtered by notification type.
    """
    recipient_version = NotificationCacheService.get_recipient_version(
        recipient_id=recipient.id,
    )
    cache_key = recipient_notification_type_list_cache_key(
        recipient_id=recipient.id,
        notification_type=notification_type,
        recipient_version=recipient_version,
    )

    def producer():
        return list(
            notification_base_queryset()
            .filter(recipient=recipient, notification_type=notification_type)
            .values_list("id", flat=True)
        )

    notification_ids = NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(
        notification_ids=notification_ids,
    ).filter(
        recipient=recipient,
        notification_type=notification_type,
    )


def list_unread_recipient_notifications(*, recipient):
    """
    List unread notifications for a specific recipient.
    """
    recipient_version = NotificationCacheService.get_recipient_version(
        recipient_id=recipient.id,
    )
    cache_key = recipient_notification_unread_list_cache_key(
        recipient_id=recipient.id,
        recipient_version=recipient_version,
    )

    def producer():
        return list(
            notification_base_queryset()
            .filter(
                recipient=recipient,
                status=Notification.STATUS_UNREAD,
            )
            .values_list("id", flat=True)
        )

    notification_ids = NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(
        notification_ids=notification_ids,
    ).filter(
        recipient=recipient,
        status=Notification.STATUS_UNREAD,
    )


def list_archived_recipient_notifications(*, recipient):
    """
    List archived notifications for a specific recipient.
    """
    recipient_version = NotificationCacheService.get_recipient_version(
        recipient_id=recipient.id,
    )
    cache_key = recipient_notification_archived_list_cache_key(
        recipient_id=recipient.id,
        recipient_version=recipient_version,
    )

    def producer():
        return list(
            notification_base_queryset()
            .filter(
                recipient=recipient,
                status=Notification.STATUS_ARCHIVED,
            )
            .values_list("id", flat=True)
        )

    notification_ids = NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(
        notification_ids=notification_ids,
    ).filter(
        recipient=recipient,
        status=Notification.STATUS_ARCHIVED,
    )


def list_notifications_by_status(*, status):
    """
    List notifications filtered by status.
    """
    management_version = NotificationCacheService.get_management_version()
    cache_key = management_notification_status_cache_key(
        status=status,
        management_version=management_version,
    )

    def producer():
        return list(
            notification_base_queryset()
            .filter(status=status)
            .values_list("id", flat=True)
        )

    notification_ids = NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(
        notification_ids=notification_ids,
    ).filter(
        status=status,
    )


def list_notifications_by_channel(*, channel):
    """
    List notifications filtered by channel.
    """
    management_version = NotificationCacheService.get_management_version()
    cache_key = management_notification_channel_cache_key(
        channel=channel,
        management_version=management_version,
    )

    def producer():
        return list(
            notification_base_queryset()
            .filter(channel=channel)
            .values_list("id", flat=True)
        )

    notification_ids = NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(
        notification_ids=notification_ids,
    ).filter(
        channel=channel,
    )


def list_notifications_by_priority(*, priority):
    """
    List notifications filtered by priority.
    """
    management_version = NotificationCacheService.get_management_version()
    cache_key = management_notification_priority_cache_key(
        priority=priority,
        management_version=management_version,
    )

    def producer():
        return list(
            notification_base_queryset()
            .filter(priority=priority)
            .values_list("id", flat=True)
        )

    notification_ids = NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(
        notification_ids=notification_ids,
    ).filter(
        priority=priority,
    )


def list_management_notifications():
    """
    List notifications for management dashboard.
    """
    management_version = NotificationCacheService.get_management_version()
    cache_key = management_notification_list_cache_key(
        management_version=management_version,
    )

    def producer():
        return list(
            notification_base_queryset()
            .values_list("id", flat=True)
        )

    notification_ids = NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_queryset_from_ids(
        notification_ids=notification_ids,
    )


def get_management_notification(*, notification_id):
    """
    Retrieve a notification by ID for management use.
    """
    notification = get_notification_by_id(notification_id=notification_id)

    management_version = NotificationCacheService.get_management_version()
    notification_version = NotificationCacheService.get_notification_version(
        notification_id=notification_id,
    )

    cache_key = management_notification_detail_cache_key(
        notification_id=notification_id,
        management_version=management_version,
        notification_version=notification_version,
    )

    def producer():
        return notification

    return NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_DEFAULT,
    )


def list_recent_notifications():
    """
    List recent notifications.
    Kept compatible with the original selector API.
    """
    return notification_base_queryset().order_by("-created_at")


def search_notifications(*, query):
    """
    Search notifications by title, message, notification type,
    source module, source event, or source object reference.
    """
    management_version = NotificationCacheService.get_management_version()
    cache_key = notification_search_cache_key(
        query=query,
        management_version=management_version,
    )

    def producer():
        return list(
            notification_base_queryset()
            .filter(
                Q(title__icontains=query)
                | Q(message__icontains=query)
                | Q(notification_type__icontains=query)
                | Q(source_module__icontains=query)
                | Q(source_event__icontains=query)
                | Q(source_object_id__icontains=query)
            )
            .values_list("id", flat=True)
        )

    notification_ids = NotificationCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=NOTIFICATION_CACHE_TIMEOUT_DEFAULT,
    )

    return _rebuild_queryset_from_ids(
        notification_ids=notification_ids,
    ).filter(
        Q(title__icontains=query)
        | Q(message__icontains=query)
        | Q(notification_type__icontains=query)
        | Q(source_module__icontains=query)
        | Q(source_event__icontains=query)
        | Q(source_object_id__icontains=query)
    )

def list_user_notifications(*, user):
    """
    Return notifications belonging to the authenticated user.
    Used by customer dashboard endpoints.
    """

    return (
        Notification.objects
        .select_related("recipient")
        .prefetch_related(
            "events",
            "deliveries",
        )
        .filter(recipient=user)
        .order_by("-created_at")
    )


def list_management_notifications():
    """
    Return all notifications for management dashboards.
    Used by staff endpoints.
    """

    return (
        Notification.objects
        .select_related("recipient", "created_by")
        .prefetch_related(
            "events",
            "deliveries",
        )
        .order_by("-created_at")
    )