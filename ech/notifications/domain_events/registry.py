from ech.notifications.domain_events.events import (
    NotificationCancelledEvent,
    NotificationCreatedEvent,
    NotificationDeliveryFailedEvent,
    NotificationDeliverySucceededEvent,
    NotificationDispatchedEvent,
    NotificationStatusChangedEvent,
)
from ech.notifications.domain_events.handlers import (
    handle_notification_cancelled,
    handle_notification_created,
    handle_notification_delivery_failed,
    handle_notification_delivery_succeeded,
    handle_notification_dispatched,
    handle_notification_status_changed,
)


EVENT_HANDLER_REGISTRY = {
    NotificationCreatedEvent: [
        handle_notification_created,
    ],
    NotificationStatusChangedEvent: [
        handle_notification_status_changed,
    ],
    NotificationCancelledEvent: [
        handle_notification_cancelled,
    ],
    NotificationDispatchedEvent: [
        handle_notification_dispatched,
    ],
    NotificationDeliverySucceededEvent: [
        handle_notification_delivery_succeeded,
    ],
    NotificationDeliveryFailedEvent: [
        handle_notification_delivery_failed,
    ],
}