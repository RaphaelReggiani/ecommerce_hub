from ech.analytics.exceptions import (
    AnalyticsShippingUnavailableException,
)
from ech.analytics.selectors import (
    get_latest_analytics_snapshot_by_period_type,
    list_shipments_for_analytics,
)
from ech.analytics.services.analytic_log_service import (
    AnalyticsLogService,
)
from ech.analytics.services.cache_service import (
    AnalyticsCacheService,
)
from ech.analytics.utils.cache_keys import (
    shipping_overview_cache_key,
)
from ech.analytics.utils.date_ranges import (
    get_period_range,
)
from ech.shipping.models import Shipment


class AnalyticsShippingOverviewService:
    """
    Service responsible for shipping analytics overview data.
    """

    @classmethod
    def get_overview(
        cls,
        *,
        period_type,
        period_start=None,
        period_end=None,
        performed_by=None,
    ):
        """
        Retrieve shipping analytics overview for the requested period.

        Snapshot data is preferred when the latest snapshot matches the
        requested bounds. Otherwise, metrics are calculated in real time.
        """

        resolved_period_start, resolved_period_end = cls._resolve_period_bounds(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
        )

        shipping_version = AnalyticsCacheService.get_shipping_version()
        cache_key = shipping_overview_cache_key(
            period_start=resolved_period_start,
            period_end=resolved_period_end,
            shipping_version=shipping_version,
        )

        def producer():
            snapshot = cls._get_matching_snapshot(
                period_type=period_type,
                period_start=resolved_period_start,
                period_end=resolved_period_end,
            )

            if snapshot is not None:
                payload = cls._build_overview_from_snapshot(snapshot=snapshot)
            else:
                payload = cls._build_overview_realtime(
                    period_start=resolved_period_start,
                    period_end=resolved_period_end,
                )

            AnalyticsLogService.log_shipping_metrics_calculated(
                period_start=resolved_period_start,
                period_end=resolved_period_end,
                shipments_delivered=payload["delivered_shipments"],
                shipments_failed=payload["failed_shipments"],
                shipments_in_transit=payload["in_transit_shipments"],
                performed_by=performed_by,
            )

            return payload

        try:
            return AnalyticsCacheService.get_or_set(
                key=cache_key,
                producer=producer,
                timeout=None,
            )
        except Exception as exc:
            raise AnalyticsShippingUnavailableException() from exc

    @classmethod
    def _resolve_period_bounds(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        """
        Resolve shipping overview period bounds.
        """

        if period_start is None and period_end is None:
            return get_period_range(period_type=period_type)

        if period_start is None or period_end is None:
            raise AnalyticsShippingUnavailableException()

        return period_start, period_end

    @classmethod
    def _get_matching_snapshot(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        """
        Return the latest snapshot only if it matches the requested period.
        """

        try:
            snapshot = get_latest_analytics_snapshot_by_period_type(
                period_type=period_type,
            )
        except Exception:
            return None

        if (
            snapshot.period_start == period_start
            and snapshot.period_end == period_end
        ):
            return snapshot

        return None

    @classmethod
    def _build_overview_from_snapshot(cls, *, snapshot):
        """
        Build shipping overview payload from a materialized snapshot.
        """

        total_shipping_operations = (
            snapshot.shipments_in_transit
            + snapshot.shipments_delivered
            + snapshot.shipments_failed
        )

        delivered_rate = 0
        failure_rate = 0
        in_transit_rate = 0

        if total_shipping_operations > 0:
            delivered_rate = (
                snapshot.shipments_delivered / total_shipping_operations
            )
            failure_rate = (
                snapshot.shipments_failed / total_shipping_operations
            )
            in_transit_rate = (
                snapshot.shipments_in_transit / total_shipping_operations
            )

        return {
            "source": "snapshot",
            "snapshot_id": snapshot.id,
            "period_type": snapshot.period_type,
            "period_start": snapshot.period_start,
            "period_end": snapshot.period_end,
            "in_transit_shipments": snapshot.shipments_in_transit,
            "delivered_shipments": snapshot.shipments_delivered,
            "failed_shipments": snapshot.shipments_failed,
            "delivered_rate": delivered_rate,
            "failure_rate": failure_rate,
            "in_transit_rate": in_transit_rate,
        }

    @classmethod
    def _build_overview_realtime(
        cls,
        *,
        period_start,
        period_end,
    ):
        """
        Build shipping overview in real time from shipment records.
        """

        shipments = list(
            list_shipments_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )

        in_transit_shipments = sum(
            1 for shipment in shipments
            if shipment.status == Shipment.STATUS_IN_TRANSIT
        )

        delivered_shipments = sum(
            1 for shipment in shipments
            if shipment.status == Shipment.STATUS_DELIVERED
        )

        failed_shipments = sum(
            1 for shipment in shipments
            if shipment.status == Shipment.STATUS_FAILED
        )

        total_shipping_operations = (
            in_transit_shipments
            + delivered_shipments
            + failed_shipments
        )

        delivered_rate = 0
        failure_rate = 0
        in_transit_rate = 0

        if total_shipping_operations > 0:
            delivered_rate = delivered_shipments / total_shipping_operations
            failure_rate = failed_shipments / total_shipping_operations
            in_transit_rate = (
                in_transit_shipments / total_shipping_operations
            )

        return {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": period_start,
            "period_end": period_end,
            "in_transit_shipments": in_transit_shipments,
            "delivered_shipments": delivered_shipments,
            "failed_shipments": failed_shipments,
            "delivered_rate": delivered_rate,
            "failure_rate": failure_rate,
            "in_transit_rate": in_transit_rate,
        }