from ech.analytics.exceptions import (
    AnalyticsUserUnavailableException,
)
from ech.analytics.selectors import (
    get_latest_analytics_snapshot_by_period_type,
    list_users_for_analytics,
)
from ech.analytics.services.analytic_log_service import (
    AnalyticsLogService,
)
from ech.analytics.services.cache_service import (
    AnalyticsCacheService,
)
from ech.analytics.utils.cache_keys import (
    user_overview_cache_key,
)
from ech.analytics.utils.date_ranges import (
    get_period_range,
)
from ech.users.models import CustomUser


class AnalyticsUserOverviewService:
    """
    Service responsible for user analytics overview data.
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
        Retrieve user analytics overview for the requested period.

        Snapshot data is preferred when the latest snapshot matches the
        requested bounds. Otherwise, metrics are calculated in real time.
        """

        resolved_period_start, resolved_period_end = cls._resolve_period_bounds(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
        )

        user_version = AnalyticsCacheService.get_user_version()
        cache_key = user_overview_cache_key(
            period_start=resolved_period_start,
            period_end=resolved_period_end,
            user_version=user_version,
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
                    period_end=resolved_period_end,
                )

            AnalyticsLogService.log_user_metrics_calculated(
                period_start=resolved_period_start,
                period_end=resolved_period_end,
                total_registered_users=payload["total_registered_users"],
                active_users=payload["active_users"],
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
            raise AnalyticsUserUnavailableException() from exc

    @classmethod
    def _resolve_period_bounds(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        if period_start is None and period_end is None:
            return get_period_range(period_type=period_type)

        if period_start is None or period_end is None:
            raise AnalyticsUserUnavailableException()

        return period_start, period_end

    @classmethod
    def _get_matching_snapshot(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
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
        return {
            "source": "snapshot",
            "snapshot_id": snapshot.id,
            "period_type": snapshot.period_type,
            "period_start": snapshot.period_start,
            "period_end": snapshot.period_end,
            "total_registered_users": snapshot.total_registered_users,
            "active_users": snapshot.active_users,
            "inactive_users": snapshot.inactive_users,
            "confirmed_users": snapshot.confirmed_users,
            "unconfirmed_users": snapshot.unconfirmed_users,
            "staff_users": snapshot.staff_users,
            "customer_users": snapshot.customer_users,
        }

    @classmethod
    def _build_overview_realtime(
        cls,
        *,
        period_end,
    ):
        users = list(
            list_users_for_analytics(
                period_end=period_end,
            )
        )

        total_registered_users = len(users)

        active_users = sum(
            1 for user in users
            if user.is_active
        )

        inactive_users = sum(
            1 for user in users
            if not user.is_active
        )

        confirmed_users = sum(
            1 for user in users
            if user.email_confirmed
        )

        unconfirmed_users = sum(
            1 for user in users
            if not user.email_confirmed
        )

        customer_users = sum(
            1 for user in users
            if user.user_role == CustomUser.ROLE_CUSTOMER_USER
        )

        staff_users = sum(
            1 for user in users
            if user.user_role != CustomUser.ROLE_CUSTOMER_USER
        )

        return {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": None,
            "period_end": period_end,
            "total_registered_users": total_registered_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "confirmed_users": confirmed_users,
            "unconfirmed_users": unconfirmed_users,
            "staff_users": staff_users,
            "customer_users": customer_users,
        }