from .logger import logger
from ech.users.utils.request_metadata import (
    get_client_ip,
    get_user_agent,
    get_request_id,
)


def log_login_success(request, user):

    logger.info(
        "login_success",
        extra={
            "user_id": user.id,
            "email": user.user_email,
            "ip_address": get_client_ip(request),
            "user_agent": get_user_agent(request),
            "request_id": get_request_id(request),
        },
    )


def log_login_failed(request, email):

    logger.warning(
        "login_failed",
        extra={
            "email": email,
            "ip_address": get_client_ip(request),
            "user_agent": get_user_agent(request),
            "request_id": get_request_id(request),
        },
    )


def log_user_registered(request, user):

    logger.info(
        "user_registered",
        extra={
            "user_id": user.id,
            "email": user.user_email,
            "ip_address": get_client_ip(request),
            "user_agent": get_user_agent(request),
            "request_id": get_request_id(request),
        },
    )


def log_email_confirmed(request, user):

    logger.info(
        "email_confirmed",
        extra={
            "user_id": user.id,
            "email": user.user_email,
            "ip_address": get_client_ip(request),
            "request_id": get_request_id(request),
        },
    )


def log_password_changed(request, user):

    logger.info(
        "password_changed",
        extra={
            "user_id": user.id,
            "ip_address": get_client_ip(request),
            "request_id": get_request_id(request),
        },
    )


def log_token_invalid(request, token_type):

    logger.warning(
        "token_invalid",
        extra={
            "token_type": token_type,
            "ip_address": get_client_ip(request),
            "user_agent": get_user_agent(request),
            "request_id": get_request_id(request),
        },
    )

def log_password_reset_requested(request, user):

    logger.info(
        "password_reset_requested",
        extra={
            "user_id": user.id,
            "email": user.user_email,
            "ip_address": get_client_ip(request),
            "user_agent": get_user_agent(request),
            "request_id": get_request_id(request),
        },
    )