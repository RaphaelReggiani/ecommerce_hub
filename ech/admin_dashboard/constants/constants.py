# ============================================================
# DASHBOARD EVENT TYPES
# ============================================================

LABEL_EVENT_TYPE_DASHBOARD_VIEWED = "dashboard_viewed"
LABEL_EVENT_TYPE_DASHBOARD_SUMMARY_FETCHED = "dashboard_summary_fetched"
LABEL_EVENT_TYPE_DASHBOARD_OPERATIONAL_METRICS_FETCHED = "dashboard_operational_metrics_fetched"
LABEL_EVENT_TYPE_DASHBOARD_RECENT_ACTIVITY_FETCHED = "dashboard_recent_activity_fetched"

# ============================================================
# BULK OPERATION EVENTS
# ============================================================

LABEL_EVENT_TYPE_ORDER_BULK_ACTION_EXECUTED = "order_bulk_action_executed"
LABEL_EVENT_TYPE_REVIEW_BULK_MODERATION_EXECUTED = "review_bulk_moderation_executed"
LABEL_EVENT_TYPE_NOTIFICATION_RETRY_EXECUTED = "notification_retry_executed"

# ============================================================
# OPERATIONAL ALERT EVENTS
# ============================================================

LABEL_EVENT_TYPE_OPERATIONAL_ALERT_TRIGGERED = "operational_alert_triggered"

# ============================================================
# DASHBOARD LIMITS
# ============================================================

DASHBOARD_RECENT_ACTIVITY_LIMIT = 25
DASHBOARD_ALERT_LIMIT = 10

# ============================================================
# BULK OPERATION SAFETY LIMITS
# ============================================================

MAX_BULK_ORDER_OPERATION = 100
MAX_BULK_REVIEW_MODERATION = 100
MAX_BULK_NOTIFICATION_RETRY = 100

# ============================================================
# OPERATIONAL ALERT THRESHOLDS
# ============================================================

PAYMENT_FAILURE_ALERT_THRESHOLD = 10
SHIPMENT_FAILURE_ALERT_THRESHOLD = 10
NOTIFICATION_FAILURE_ALERT_THRESHOLD = 20
LOW_STOCK_ALERT_THRESHOLD = 5

# ============================================================
# CACHE TTL (SECONDS)
# ============================================================

DASHBOARD_SUMMARY_CACHE_TTL = 60
DASHBOARD_OPERATIONAL_METRICS_CACHE_TTL = 60
DASHBOARD_RECENT_ACTIVITY_CACHE_TTL = 30
DASHBOARD_ALERT_CACHE_TTL = 30