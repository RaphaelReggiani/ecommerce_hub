from ech.admin_dashboard.domain_events.events import (
    AdminDashboardAccessedEvent,
    AdminBulkOrderActionExecutedEvent,
    AdminBulkOrderActionFailedEvent,
    AdminBulkReviewModerationExecutedEvent,
    AdminBulkReviewModerationFailedEvent,
    AdminNotificationRetryExecutedEvent,
    AdminNotificationRetryFailedEvent,
    AdminDashboardAlertGeneratedEvent,
)

from ech.admin_dashboard.domain_events.handlers import (
    handle_admin_dashboard_accessed,
    handle_admin_bulk_order_action_executed,
    handle_admin_bulk_order_action_failed,
    handle_admin_bulk_review_moderation_executed,
    handle_admin_bulk_review_moderation_failed,
    handle_admin_notification_retry_executed,
    handle_admin_notification_retry_failed,
    handle_admin_dashboard_alert_generated,
)


EVENT_HANDLER_REGISTRY = {
    AdminDashboardAccessedEvent: [
        handle_admin_dashboard_accessed,
    ],
    AdminBulkOrderActionExecutedEvent: [
        handle_admin_bulk_order_action_executed,
    ],
    AdminBulkOrderActionFailedEvent: [
        handle_admin_bulk_order_action_failed,
    ],
    AdminBulkReviewModerationExecutedEvent: [
        handle_admin_bulk_review_moderation_executed,
    ],
    AdminBulkReviewModerationFailedEvent: [
        handle_admin_bulk_review_moderation_failed,
    ],
    AdminNotificationRetryExecutedEvent: [
        handle_admin_notification_retry_executed,
    ],
    AdminNotificationRetryFailedEvent: [
        handle_admin_notification_retry_failed,
    ],
    AdminDashboardAlertGeneratedEvent: [
        handle_admin_dashboard_alert_generated,
    ],
}