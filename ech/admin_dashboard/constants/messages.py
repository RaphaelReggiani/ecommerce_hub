# =============================
# DASHBOARD ACCESS
# =============================

ADMIN_DASHBOARD_RETRIEVED = "Admin dashboard retrieved successfully."
ADMIN_DASHBOARD_ACCESS_DENIED = "You do not have permission to access the admin dashboard."
ADMIN_DASHBOARD_DATA_UNAVAILABLE = "Admin dashboard data is currently unavailable."


# =============================
# DASHBOARD SUMMARY
# =============================

ADMIN_DASHBOARD_SUMMARY_RETRIEVED = "Dashboard summary metrics retrieved successfully."
ADMIN_DASHBOARD_SUMMARY_UNAVAILABLE = "Dashboard summary metrics are unavailable."


# =============================
# OPERATIONAL METRICS
# =============================

ADMIN_OPERATIONAL_METRICS_RETRIEVED = "Operational metrics retrieved successfully."
ADMIN_OPERATIONAL_METRICS_UNAVAILABLE = "Operational metrics are unavailable."


# =============================
# RECENT ACTIVITY
# =============================

ADMIN_RECENT_ACTIVITY_RETRIEVED = "Recent system activity retrieved successfully."
ADMIN_RECENT_ACTIVITY_UNAVAILABLE = "Recent system activity is unavailable."


# =============================
# OPERATIONAL ALERTS
# =============================

ADMIN_OPERATIONAL_ALERTS_RETRIEVED = "Operational alerts retrieved successfully."
ADMIN_OPERATIONAL_ALERTS_UNAVAILABLE = "Operational alerts are unavailable."


# =============================
# BULK ORDER OPERATIONS
# =============================

ADMIN_ORDER_BULK_ACTION_STARTED = "Bulk order operation started."
ADMIN_ORDER_BULK_ACTION_COMPLETED = "Bulk order operation completed successfully."
ADMIN_ORDER_BULK_ACTION_FAILED = "Bulk order operation failed."
ADMIN_ORDER_BULK_ACTION_PERMISSION_DENIED = "You do not have permission to perform bulk order operations."
ADMIN_ORDER_BULK_LIMIT_EXCEEDED = "Bulk order operation exceeds the allowed limit."


# =============================
# BULK REVIEW MODERATION
# =============================

ADMIN_REVIEW_BULK_MODERATION_STARTED = "Bulk review moderation started."
ADMIN_REVIEW_BULK_MODERATION_COMPLETED = "Bulk review moderation completed successfully."
ADMIN_REVIEW_BULK_MODERATION_FAILED = "Bulk review moderation failed."
ADMIN_REVIEW_BULK_MODERATION_PERMISSION_DENIED = "You do not have permission to moderate reviews."
ADMIN_REVIEW_BULK_LIMIT_EXCEEDED = "Bulk review moderation exceeds the allowed limit."


# =============================
# BULK NOTIFICATION RETRY
# =============================

ADMIN_NOTIFICATION_RETRY_STARTED = "Notification retry process started."
ADMIN_NOTIFICATION_RETRY_COMPLETED = "Notification retry completed successfully."
ADMIN_NOTIFICATION_RETRY_FAILED = "Notification retry failed."
ADMIN_NOTIFICATION_RETRY_PERMISSION_DENIED = "You do not have permission to retry notifications."
ADMIN_NOTIFICATION_RETRY_LIMIT_EXCEEDED = "Notification retry exceeds the allowed limit."


# =============================
# CACHE
# =============================

ADMIN_DASHBOARD_CACHE_HIT = "Dashboard data retrieved from cache."
ADMIN_DASHBOARD_CACHE_MISS = "Dashboard cache miss. Data recomputed."
ADMIN_DASHBOARD_CACHE_INVALIDATED = "Dashboard cache invalidated."


# =============================
# LOGGING
# =============================

LOG_ADMIN_DASHBOARD_VIEWED = "Admin dashboard viewed."
LOG_ADMIN_DASHBOARD_SUMMARY_FETCHED = "Admin dashboard summary retrieved."
LOG_ADMIN_OPERATIONAL_METRICS_FETCHED = "Admin operational metrics retrieved."
LOG_ADMIN_RECENT_ACTIVITY_FETCHED = "Admin recent activity retrieved."
LOG_ADMIN_ALERTS_FETCHED = "Admin operational alerts retrieved."

LOG_ADMIN_ORDER_BULK_ACTION = "Admin bulk order action executed."
LOG_ADMIN_REVIEW_BULK_MODERATION = "Admin bulk review moderation executed."
LOG_ADMIN_NOTIFICATION_RETRY = "Admin notification retry executed."

LOG_ADMIN_CACHE_INVALIDATED = "Admin dashboard cache invalidated."


# =============================
# IDEMPOTENCY
# =============================

ADMIN_IDEMPOTENCY_KEY_CONFLICT = (
    "This idempotency key has already been used for a different admin dashboard request."
)