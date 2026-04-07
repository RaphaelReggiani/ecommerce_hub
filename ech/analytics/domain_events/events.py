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


class AnalyticsSnapshotCreatedEvent(BaseDomainEvent):
    """
    Event triggered when an analytics snapshot is created.
    """

    event_name = "analytics_snapshot_created"

    def __init__(
        self,
        *,
        snapshot_id,
        period_type,
        period_start,
        period_end,
        generated_by_id=None,
    ):
        self.snapshot_id = snapshot_id
        self.period_type = period_type
        self.period_start = period_start
        self.period_end = period_end
        self.generated_by_id = generated_by_id


class AnalyticsSnapshotRefreshedEvent(BaseDomainEvent):
    """
    Event triggered when an analytics snapshot is refreshed.
    """

    event_name = "analytics_snapshot_refreshed"

    def __init__(
        self,
        *,
        snapshot_id,
        period_type,
        period_start,
        period_end,
        refreshed_by_id=None,
    ):
        self.snapshot_id = snapshot_id
        self.period_type = period_type
        self.period_start = period_start
        self.period_end = period_end
        self.refreshed_by_id = refreshed_by_id


class AnalyticsSnapshotFailedEvent(BaseDomainEvent):
    """
    Event triggered when analytics snapshot generation or refresh fails.
    """

    event_name = "analytics_snapshot_failed"

    def __init__(
        self,
        *,
        snapshot_id=None,
        period_type,
        period_start,
        period_end,
        error_message,
        performed_by_id=None,
    ):
        self.snapshot_id = snapshot_id
        self.period_type = period_type
        self.period_start = period_start
        self.period_end = period_end
        self.error_message = error_message
        self.performed_by_id = performed_by_id