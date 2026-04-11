class BaseDomainEvent:
    """
    Base domain event for the admin dashboard domain.
    """

    event_name = "base_domain_event"

    def to_dict(self):
        """
        Serialize event payload for logging, debugging, or handlers.
        """
        return self.__dict__.copy()


class AdminDashboardAccessedEvent(BaseDomainEvent):
    """
    Event triggered when the admin dashboard is accessed.
    """

    event_name = "admin_dashboard_accessed"

    def __init__(
        self,
        *,
        user_id,
    ):
        self.user_id = user_id


class AdminBulkOrderActionExecutedEvent(BaseDomainEvent):
    """
    Event triggered when a bulk order action is executed.
    """

    event_name = "admin_bulk_order_action_executed"

    def __init__(
        self,
        *,
        action_type,
        order_ids,
        performed_by_id,
    ):
        self.action_type = action_type
        self.order_ids = order_ids
        self.performed_by_id = performed_by_id


class AdminBulkOrderActionFailedEvent(BaseDomainEvent):
    """
    Event triggered when a bulk order action fails.
    """

    event_name = "admin_bulk_order_action_failed"

    def __init__(
        self,
        *,
        action_type,
        order_ids,
        error_message,
        performed_by_id=None,
    ):
        self.action_type = action_type
        self.order_ids = order_ids
        self.error_message = error_message
        self.performed_by_id = performed_by_id


class AdminBulkReviewModerationExecutedEvent(BaseDomainEvent):
    """
    Event triggered when bulk review moderation is executed.
    """

    event_name = "admin_bulk_review_moderation_executed"

    def __init__(
        self,
        *,
        moderation_action,
        review_ids,
        performed_by_id,
    ):
        self.moderation_action = moderation_action
        self.review_ids = review_ids
        self.performed_by_id = performed_by_id


class AdminBulkReviewModerationFailedEvent(BaseDomainEvent):
    """
    Event triggered when bulk review moderation fails.
    """

    event_name = "admin_bulk_review_moderation_failed"

    def __init__(
        self,
        *,
        moderation_action,
        review_ids,
        error_message,
        performed_by_id=None,
    ):
        self.moderation_action = moderation_action
        self.review_ids = review_ids
        self.error_message = error_message
        self.performed_by_id = performed_by_id


class AdminNotificationRetryExecutedEvent(BaseDomainEvent):
    """
    Event triggered when notification retry is executed.
    """

    event_name = "admin_notification_retry_executed"

    def __init__(
        self,
        *,
        notification_ids,
        performed_by_id,
    ):
        self.notification_ids = notification_ids
        self.performed_by_id = performed_by_id


class AdminNotificationRetryFailedEvent(BaseDomainEvent):
    """
    Event triggered when notification retry fails.
    """

    event_name = "admin_notification_retry_failed"

    def __init__(
        self,
        *,
        notification_ids,
        error_message,
        performed_by_id=None,
    ):
        self.notification_ids = notification_ids
        self.error_message = error_message
        self.performed_by_id = performed_by_id


class AdminDashboardAlertGeneratedEvent(BaseDomainEvent):
    """
    Event triggered when a dashboard alert is generated.
    """

    event_name = "admin_dashboard_alert_generated"

    def __init__(
        self,
        *,
        alert_type,
        alert_message,
        metadata=None,
    ):
        self.alert_type = alert_type
        self.alert_message = alert_message
        self.metadata = metadata or {}