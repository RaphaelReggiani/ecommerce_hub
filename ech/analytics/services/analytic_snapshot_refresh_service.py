from django.db import transaction
from django.utils import timezone

from ech.analytics.domain_events.dispatcher import DomainEventDispatcher
from ech.analytics.domain_events.events import (
    AnalyticsSnapshotRefreshedEvent,
    AnalyticsSnapshotFailedEvent,
)
from ech.analytics.exceptions import (
    AnalyticsSnapshotRefreshException,
    AnalyticsSnapshotRefreshNotAllowedException,
)
from ech.analytics.models import (
    AnalyticsEvent,
)
from ech.analytics.services.analytic_log_service import (
    AnalyticsLogService,
)
from ech.analytics.services.analytic_snapshot_generation_service import (
    AnalyticsSnapshotGenerationService,
)
from ech.analytics.services.cache_service import (
    AnalyticsCacheService,
)


class AnalyticsSnapshotRefreshService:
    """
    Service responsible for analytics snapshot refresh operations.
    """

    @classmethod
    @transaction.atomic
    def refresh_snapshot(
        cls,
        *,
        snapshot,
        performed_by=None,
        metadata=None,
    ):
        """
        Refresh an existing analytics snapshot by rebuilding its metrics.

        Args:
            snapshot: AnalyticsSnapshot instance.
            performed_by: Optional user performing the action.
            metadata: Optional metadata payload.

        Returns:
            AnalyticsSnapshot: Refreshed snapshot.

        Raises:
            AnalyticsSnapshotRefreshNotAllowedException:
                If refresh is not allowed for the given snapshot.
            AnalyticsSnapshotRefreshException:
                If refresh fails.
        """

        cls._validate_refresh_allowed(snapshot=snapshot)

        try:
            cls._create_event(
                snapshot=snapshot,
                event_type=AnalyticsEvent.TYPE_SNAPSHOT_GENERATION_STARTED,
                performed_by=performed_by,
                metadata={
                    "operation": "refresh",
                    **(metadata or {}),
                },
            )

            metrics = AnalyticsSnapshotGenerationService._build_snapshot_metrics(
                period_start=snapshot.period_start,
                period_end=snapshot.period_end,
            )

            AnalyticsSnapshotGenerationService._apply_metrics(
                snapshot=snapshot,
                metrics=metrics,
            )

            lifecycle = snapshot.lifecycle
            lifecycle.refreshed_at = timezone.now()
            lifecycle.save(
                update_fields=[
                    "refreshed_at",
                    "updated_at",
                ]
            )

            cls._create_event(
                snapshot=snapshot,
                event_type=AnalyticsEvent.TYPE_SNAPSHOT_REFRESHED,
                performed_by=performed_by,
                metadata=metadata,
            )

            AnalyticsLogService.log_snapshot_refreshed(
                snapshot=snapshot,
                performed_by=performed_by,
            )

            AnalyticsLogService.log_snapshot_metrics_updated(
                snapshot=snapshot,
                updated_fields=list(metrics.keys()),
                performed_by=performed_by,
            )

            DomainEventDispatcher.dispatch(
                AnalyticsSnapshotRefreshedEvent(
                    snapshot_id=snapshot.id,
                    period_type=snapshot.period_type,
                    period_start=snapshot.period_start,
                    period_end=snapshot.period_end,
                    refreshed_by_id=getattr(performed_by, "id", None),
                )
            )

            transaction.on_commit(
                lambda: AnalyticsCacheService.invalidate_after_snapshot_mutation(
                    snapshot_id=snapshot.id,
                    period_type=snapshot.period_type,
                )
            )

            return snapshot

        except Exception as exc:
            cls._mark_refresh_failure(snapshot=snapshot)

            cls._create_event(
                snapshot=snapshot,
                event_type=AnalyticsEvent.TYPE_SNAPSHOT_FAILED,
                performed_by=performed_by,
                metadata={
                    "operation": "refresh",
                    "error_message": str(exc),
                    **(metadata or {}),
                },
            )

            DomainEventDispatcher.dispatch(
                AnalyticsSnapshotFailedEvent(
                    snapshot_id=snapshot.id,
                    period_type=snapshot.period_type,
                    period_start=snapshot.period_start,
                    period_end=snapshot.period_end,
                    error_message=str(exc),
                    performed_by_id=getattr(performed_by, "id", None),
                )
            )

            raise AnalyticsSnapshotRefreshException() from exc

    @classmethod
    def _validate_refresh_allowed(cls, *, snapshot):
        """
        Validate whether snapshot refresh is allowed.
        """

        if snapshot is None:
            raise AnalyticsSnapshotRefreshNotAllowedException()

        lifecycle = getattr(snapshot, "lifecycle", None)

        if lifecycle is None:
            raise AnalyticsSnapshotRefreshNotAllowedException()

    @classmethod
    def _mark_refresh_failure(cls, *, snapshot):
        """
        Mark refresh failure timestamp in snapshot lifecycle.
        """

        lifecycle = getattr(snapshot, "lifecycle", None)

        if lifecycle is None:
            return

        lifecycle.failed_at = timezone.now()
        lifecycle.save(
            update_fields=[
                "failed_at",
                "updated_at",
            ]
        )

    @classmethod
    def _create_event(
        cls,
        *,
        snapshot,
        event_type,
        performed_by=None,
        metadata=None,
    ):
        """
        Create analytics audit event.
        """

        AnalyticsEvent.objects.create(
            snapshot=snapshot,
            event_type=event_type,
            performed_by=performed_by,
            metadata=metadata or {},
        )