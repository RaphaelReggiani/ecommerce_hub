class BaseDomainEvent:
    """
    Base domain event.
    """

    event_name = "base_domain_event"

    def to_dict(self):
        """
        Serialize event payload for logging, debugging, or handlers.
        """

        return self.__dict__.copy()


class NotificationCreatedEvent(BaseDomainEvent):
    """
    Event triggered when a notification is created.
    """

    event_name = "notification_created"

    def __init__(
        self,
        *,
        notification_id,
        recipient_id,
        notification_type,
        channel,
        performed_by_id=None,
    ):
        self.notification_id = notification_id
        self.recipient_id = recipient_id
        self.notification_type = notification_type
        self.channel = channel
        self.performed_by_id = performed_by_id


class NotificationStatusChangedEvent(BaseDomainEvent):
    """
    Event triggered when a notification status changes.
    """

    event_name = "notification_status_changed"

    def __init__(
        self,
        *,
        notification_id,
        previous_status,
        new_status,
        performed_by_id=None,
    ):
        self.notification_id = notification_id
        self.previous_status = previous_status
        self.new_status = new_status
        self.performed_by_id = performed_by_id


class NotificationCancelledEvent(BaseDomainEvent):
    """
    Event triggered when a notification is cancelled.
    """

    event_name = "notification_cancelled"

    def __init__(
        self,
        *,
        notification_id,
        recipient_id,
        performed_by_id=None,
    ):
        self.notification_id = notification_id
        self.recipient_id = recipient_id
        self.performed_by_id = performed_by_id


class NotificationDispatchedEvent(BaseDomainEvent):
    """
    Event triggered when a notification dispatch process starts.
    """

    event_name = "notification_dispatched"

    def __init__(
        self,
        *,
        notification_id,
        recipient_id,
        channel,
        performed_by_id=None,
    ):
        self.notification_id = notification_id
        self.recipient_id = recipient_id
        self.channel = channel
        self.performed_by_id = performed_by_id


class NotificationDeliverySucceededEvent(BaseDomainEvent):
    """
    Event triggered when a notification delivery succeeds.
    """

    event_name = "notification_delivery_succeeded"

    def __init__(
        self,
        *,
        notification_id,
        delivery_id,
        recipient_id,
        channel,
        performed_by_id=None,
    ):
        self.notification_id = notification_id
        self.delivery_id = delivery_id
        self.recipient_id = recipient_id
        self.channel = channel
        self.performed_by_id = performed_by_id


class NotificationDeliveryFailedEvent(BaseDomainEvent):
    """
    Event triggered when a notification delivery fails.
    """

    event_name = "notification_delivery_failed"

    def __init__(
        self,
        *,
        notification_id,
        delivery_id,
        recipient_id,
        channel,
        performed_by_id=None,
    ):
        self.notification_id = notification_id
        self.delivery_id = delivery_id
        self.recipient_id = recipient_id
        self.channel = channel
        self.performed_by_id = performed_by_id