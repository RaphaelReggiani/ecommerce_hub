import logging


logger = logging.getLogger(__name__)


class UserLogService:
    """
    Service responsible for structured user domain logs.
    """

    @staticmethod
    def log_user_registered(*, user, performed_by=None):
        """
        Log user registration.
        """

        logger.info(
            "User registered.",
            extra={
                "user_id": str(user.id),
                "email": user.user_email,
                "role": user.user_role,
                "is_active": user.is_active,
                "email_confirmed": user.email_confirmed,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_user_email_confirmed(*, user, performed_by=None):
        """
        Log email confirmation.
        """

        logger.info(
            "User email confirmed.",
            extra={
                "user_id": str(user.id),
                "email": user.user_email,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_user_profile_updated(
        *,
        user,
        changed_fields=None,
        performed_by=None,
    ):
        """
        Log user profile update.
        """

        logger.info(
            "User profile updated.",
            extra={
                "user_id": str(user.id),
                "email": user.user_email,
                "changed_fields": changed_fields or [],
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_user_password_changed(*, user, performed_by=None):
        """
        Log password change.
        """

        logger.info(
            "User password changed.",
            extra={
                "user_id": str(user.id),
                "email": user.user_email,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_user_login_succeeded(*, user):
        """
        Log successful login.
        """

        logger.info(
            "User login succeeded.",
            extra={
                "user_id": str(user.id),
                "email": user.user_email,
            },
        )

    @staticmethod
    def log_user_login_failed(*, email):
        """
        Log failed login attempt.
        """

        logger.warning(
            "User login failed.",
            extra={
                "email": email,
            },
        )