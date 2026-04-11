"""
Role access management for the Admin Dashboard module.

This module centralizes role-based access definitions used by the
Admin Dashboard services, API permissions, and operational controls.

Roles are imported directly from the CustomUser model to ensure
consistency with the system's core authentication domain.
"""

from ech.users.models import CustomUser


# ============================================================
# BASE DASHBOARD ACCESS
# ============================================================

"""
Roles allowed to access the Admin Dashboard interface.

This does not automatically grant permission to perform
administrative actions — it only grants visibility access.
"""

ALLOWED_ADMIN_DASHBOARD_ACCESS_ROLES = {
    CustomUser.ROLE_SUPERADMIN,
    CustomUser.ROLE_ADMIN,
    CustomUser.ROLE_PAYMENT_STAFF,
    CustomUser.ROLE_OPERATIONS_STAFF,
    CustomUser.ROLE_SUPPORT_STAFF,
    CustomUser.ROLE_ANALYTICS_STAFF,
}


"""
Roles allowed to retrieve high-level dashboard summary metrics.
"""

ALLOWED_DASHBOARD_SUMMARY_ROLES = ALLOWED_ADMIN_DASHBOARD_ACCESS_ROLES


# ============================================================
# ORDER OPERATION CONTROLS
# ============================================================

"""
Roles allowed to execute bulk operational actions on orders.
"""

ALLOWED_ORDER_BULK_ACTION_ROLES = {
    CustomUser.ROLE_SUPERADMIN,
    CustomUser.ROLE_ADMIN,
    CustomUser.ROLE_OPERATIONS_STAFF,
}


# ============================================================
# REVIEW MODERATION CONTROLS
# ============================================================

"""
Roles allowed to perform bulk moderation actions on reviews.
"""

ALLOWED_REVIEW_BULK_MODERATION_ROLES = {
    CustomUser.ROLE_SUPERADMIN,
    CustomUser.ROLE_ADMIN,
    CustomUser.ROLE_SUPPORT_STAFF,
}


# ============================================================
# NOTIFICATION OPERATIONAL CONTROLS
# ============================================================

"""
Roles allowed to retry failed notification deliveries.
"""

ALLOWED_NOTIFICATION_RETRY_ROLES = {
    CustomUser.ROLE_SUPERADMIN,
    CustomUser.ROLE_ADMIN,
    CustomUser.ROLE_SUPPORT_STAFF,
}


# ============================================================
# PAYMENT OPERATIONAL MONITORING
# ============================================================

"""
Roles allowed to access payment operational metrics and monitoring.
"""

ALLOWED_PAYMENT_OPERATIONAL_ROLES = {
    CustomUser.ROLE_SUPERADMIN,
    CustomUser.ROLE_ADMIN,
    CustomUser.ROLE_PAYMENT_STAFF,
}


# ============================================================
# ANALYTICS CONTROLS
# ============================================================

"""
Roles allowed to manage analytics-related operations
such as snapshot generation and refresh.
"""

ALLOWED_ANALYTICS_CONTROL_ROLES = {
    CustomUser.ROLE_SUPERADMIN,
    CustomUser.ROLE_ADMIN,
    CustomUser.ROLE_ANALYTICS_STAFF,
}