from ech.notifications.constants.cache import (
    NOTIFICATION_CACHE_DETAIL_PREFIX,
    NOTIFICATION_CACHE_RECIPIENT_LIST_PREFIX,
    NOTIFICATION_CACHE_MANAGEMENT_LIST_PREFIX,
    NOTIFICATION_CACHE_SEARCH_PREFIX,
    NOTIFICATION_CACHE_NOTIFICATION_VERSION_PREFIX,
    NOTIFICATION_CACHE_RECIPIENT_VERSION_PREFIX,
    NOTIFICATION_CACHE_MANAGEMENT_VERSION_PREFIX,
)


def _normalize_text(value):
    """
    Normalize text values for cache keys.
    """
    if value is None:
        return "none"

    return str(value).strip().lower().replace(" ", "_")


def notification_version_key(*, notification_id):
    return f"{NOTIFICATION_CACHE_NOTIFICATION_VERSION_PREFIX}:{notification_id}"


def recipient_version_key(*, recipient_id):
    return f"{NOTIFICATION_CACHE_RECIPIENT_VERSION_PREFIX}:{recipient_id}"


def management_version_key():
    return f"{NOTIFICATION_CACHE_MANAGEMENT_VERSION_PREFIX}"


def notification_detail_cache_key(*, notification_id, notification_version):
    return (
        f"{NOTIFICATION_CACHE_DETAIL_PREFIX}:notification:{notification_id}:"
        f"v{notification_version}"
    )


def recipient_notification_detail_cache_key(
    *,
    recipient_id,
    notification_id,
    recipient_version,
    notification_version,
):
    return (
        f"{NOTIFICATION_CACHE_RECIPIENT_LIST_PREFIX}:{recipient_id}:notification:{notification_id}:"
        f"rv{recipient_version}:nv{notification_version}"
    )


def management_notification_detail_cache_key(
    *,
    notification_id,
    management_version,
    notification_version,
):
    return (
        f"{NOTIFICATION_CACHE_MANAGEMENT_LIST_PREFIX}:notification:{notification_id}:"
        f"mv{management_version}:nv{notification_version}"
    )


def recipient_notification_list_cache_key(*, recipient_id, recipient_version):
    return (
        f"{NOTIFICATION_CACHE_RECIPIENT_LIST_PREFIX}:{recipient_id}:list:"
        f"v{recipient_version}"
    )


def recipient_notification_status_list_cache_key(
    *,
    recipient_id,
    status,
    recipient_version,
):
    return (
        f"{NOTIFICATION_CACHE_RECIPIENT_LIST_PREFIX}:{recipient_id}:status:"
        f"{_normalize_text(status)}:v{recipient_version}"
    )


def recipient_notification_type_list_cache_key(
    *,
    recipient_id,
    notification_type,
    recipient_version,
):
    return (
        f"{NOTIFICATION_CACHE_RECIPIENT_LIST_PREFIX}:{recipient_id}:type:"
        f"{_normalize_text(notification_type)}:v{recipient_version}"
    )


def recipient_notification_unread_list_cache_key(
    *,
    recipient_id,
    recipient_version,
):
    return (
        f"{NOTIFICATION_CACHE_RECIPIENT_LIST_PREFIX}:{recipient_id}:unread:"
        f"v{recipient_version}"
    )


def recipient_notification_archived_list_cache_key(
    *,
    recipient_id,
    recipient_version,
):
    return (
        f"{NOTIFICATION_CACHE_RECIPIENT_LIST_PREFIX}:{recipient_id}:archived:"
        f"v{recipient_version}"
    )


def management_notification_list_cache_key(*, management_version):
    return (
        f"{NOTIFICATION_CACHE_MANAGEMENT_LIST_PREFIX}:list:"
        f"v{management_version}"
    )


def management_notification_status_cache_key(*, status, management_version):
    return (
        f"{NOTIFICATION_CACHE_MANAGEMENT_LIST_PREFIX}:status:"
        f"{_normalize_text(status)}:v{management_version}"
    )


def management_notification_channel_cache_key(*, channel, management_version):
    return (
        f"{NOTIFICATION_CACHE_MANAGEMENT_LIST_PREFIX}:channel:"
        f"{_normalize_text(channel)}:v{management_version}"
    )


def management_notification_priority_cache_key(*, priority, management_version):
    return (
        f"{NOTIFICATION_CACHE_MANAGEMENT_LIST_PREFIX}:priority:"
        f"{_normalize_text(priority)}:v{management_version}"
    )


def notification_search_cache_key(*, query, management_version):
    return (
        f"{NOTIFICATION_CACHE_SEARCH_PREFIX}:{_normalize_text(query)}:"
        f"v{management_version}"
    )