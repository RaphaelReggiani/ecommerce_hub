from ech.analytics.domain_events.events import (
    AnalyticsSnapshotCreatedEvent,
    AnalyticsSnapshotRefreshedEvent,
    AnalyticsSnapshotFailedEvent,
)
from ech.analytics.domain_events.handlers import (
    handle_analytics_snapshot_created,
    handle_analytics_snapshot_refreshed,
    handle_analytics_snapshot_failed,
)


EVENT_HANDLER_REGISTRY = {
    AnalyticsSnapshotCreatedEvent: [
        handle_analytics_snapshot_created,
    ],
    AnalyticsSnapshotRefreshedEvent: [
        handle_analytics_snapshot_refreshed,
    ],
    AnalyticsSnapshotFailedEvent: [
        handle_analytics_snapshot_failed,
    ],
}