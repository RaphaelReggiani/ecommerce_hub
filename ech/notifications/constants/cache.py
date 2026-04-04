# ============================================================
# CACHE PREFIXES
# ============================================================

NOTIFICATION_CACHE_PREFIX = "notification"

# ============================================================
# CACHE VERSION PREFIXES
# ============================================================

NOTIFICATION_CACHE_VERSION_PREFIX = f"{NOTIFICATION_CACHE_PREFIX}:version"
NOTIFICATION_CACHE_NOTIFICATION_VERSION_PREFIX = (
    f"{NOTIFICATION_CACHE_VERSION_PREFIX}:notification"
)
NOTIFICATION_CACHE_RECIPIENT_VERSION_PREFIX = (
    f"{NOTIFICATION_CACHE_VERSION_PREFIX}:recipient"
)
NOTIFICATION_CACHE_MANAGEMENT_VERSION_PREFIX = (
    f"{NOTIFICATION_CACHE_VERSION_PREFIX}:management"
)

# ============================================================
# CACHE DETAIL PREFIXES
# ============================================================

NOTIFICATION_CACHE_DETAIL_PREFIX = f"{NOTIFICATION_CACHE_PREFIX}:detail"
NOTIFICATION_CACHE_RECIPIENT_DETAIL_PREFIX = (
    f"{NOTIFICATION_CACHE_PREFIX}:recipient:detail"
)
NOTIFICATION_CACHE_MANAGEMENT_DETAIL_PREFIX = (
    f"{NOTIFICATION_CACHE_PREFIX}:management:detail"
)

# ============================================================
# CACHE LIST PREFIXES
# ============================================================

NOTIFICATION_CACHE_RECIPIENT_LIST_PREFIX = (
    f"{NOTIFICATION_CACHE_PREFIX}:recipient:list"
)
NOTIFICATION_CACHE_RECIPIENT_STATUS_LIST_PREFIX = (
    f"{NOTIFICATION_CACHE_PREFIX}:recipient:status:list"
)
NOTIFICATION_CACHE_RECIPIENT_TYPE_LIST_PREFIX = (
    f"{NOTIFICATION_CACHE_PREFIX}:recipient:type:list"
)
NOTIFICATION_CACHE_RECIPIENT_UNREAD_LIST_PREFIX = (
    f"{NOTIFICATION_CACHE_PREFIX}:recipient:unread:list"
)
NOTIFICATION_CACHE_RECIPIENT_ARCHIVED_LIST_PREFIX = (
    f"{NOTIFICATION_CACHE_PREFIX}:recipient:archived:list"
)

NOTIFICATION_CACHE_MANAGEMENT_LIST_PREFIX = (
    f"{NOTIFICATION_CACHE_PREFIX}:management:list"
)
NOTIFICATION_CACHE_MANAGEMENT_STATUS_LIST_PREFIX = (
    f"{NOTIFICATION_CACHE_PREFIX}:management:status:list"
)
NOTIFICATION_CACHE_MANAGEMENT_CHANNEL_LIST_PREFIX = (
    f"{NOTIFICATION_CACHE_PREFIX}:management:channel:list"
)
NOTIFICATION_CACHE_MANAGEMENT_PRIORITY_LIST_PREFIX = (
    f"{NOTIFICATION_CACHE_PREFIX}:management:priority:list"
)

# ============================================================
# CACHE SEARCH PREFIXES
# ============================================================

NOTIFICATION_CACHE_SEARCH_PREFIX = f"{NOTIFICATION_CACHE_PREFIX}:search"

# ============================================================
# CACHE TIMEOUTS
# ============================================================

NOTIFICATION_CACHE_TIMEOUT_SHORT = 60
NOTIFICATION_CACHE_TIMEOUT_DEFAULT = 300
NOTIFICATION_CACHE_TIMEOUT_LONG = 900

# ============================================================
# CACHE VERSION DEFAULTS
# ============================================================

NOTIFICATION_CACHE_DEFAULT_VERSION = 1

