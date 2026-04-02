import logging


logger = logging.getLogger(__name__)


def handle_user_registered(event):
    """
    Handle user registered event.

    Focused on observability. Can later be expanded to:
    - analytics tracking
    - audit trail
    - security monitoring
    """

    logger.info(
        "Handled user registered domain event.",
        extra={
            "event_name": event.event_name,
            "user_id": str(event.user_id),
            "email": event.email,
            "role": event.role,
            "performed_by_id": event.performed_by_id,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "request_id": event.request_id,
        },
    )


def handle_user_email_confirmed(event):
    """
    Handle email confirmation event.
    """

    logger.info(
        "Handled user email confirmed domain event.",
        extra={
            "event_name": event.event_name,
            "user_id": str(event.user_id),
            "email": event.email,
            "performed_by_id": event.performed_by_id,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "request_id": event.request_id,
        },
    )


def handle_user_password_reset_requested(event):
    """
    Handle password reset request event.
    """

    logger.info(
        "Handled user password reset requested domain event.",
        extra={
            "event_name": event.event_name,
            "user_id": str(event.user_id),
            "email": event.email,
            "performed_by_id": event.performed_by_id,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "request_id": event.request_id,
        },
    )


def handle_user_password_changed(event):
    """
    Handle password changed event.
    """

    logger.info(
        "Handled user password changed domain event.",
        extra={
            "event_name": event.event_name,
            "user_id": str(event.user_id),
            "performed_by_id": event.performed_by_id,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "request_id": event.request_id,
        },
    )


def handle_user_login_succeeded(event):
    """
    Handle successful login event.
    """

    logger.info(
        "Handled user login succeeded domain event.",
        extra={
            "event_name": event.event_name,
            "user_id": str(event.user_id),
            "email": event.email,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "request_id": event.request_id,
        },
    )


def handle_user_login_failed(event):
    """
    Handle failed login event.
    """

    logger.warning(
        "Handled user login failed domain event.",
        extra={
            "event_name": event.event_name,
            "email": event.email,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "request_id": event.request_id,
        },
    )


def handle_user_token_invalid(event):
    """
    Handle invalid token usage.
    """

    logger.warning(
        "Handled user invalid token domain event.",
        extra={
            "event_name": event.event_name,
            "token_type": event.token_type,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "request_id": event.request_id,
        },
    )