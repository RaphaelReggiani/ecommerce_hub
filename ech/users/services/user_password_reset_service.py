from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse

from ech.users.constants.constants import PASSWORD_RESET_EXPIRATION_HOURS
from ech.users.exceptions import TokenExpiredError, TokenInvalidError
from ech.users.models import UserToken
from ech.users.selectors import get_user_by_email, get_valid_token

User = get_user_model()


class PasswordResetService:
    """
    Handles password reset request and password reset execution.
    """

    @staticmethod
    @transaction.atomic
    def request_password_reset(email: str):
        """
        Always returns success to prevent user enumeration.

        The flow is functionally idempotent from an API perspective:
        previous reset tokens are removed and only the latest one remains valid.
        """

        user = get_user_by_email(email)

        if not user or not user.is_active:
            return

        UserToken.objects.filter(
            user=user,
            token_type=UserToken.TYPE_PASSWORD_RESET,
        ).delete()

        token_obj = UserToken.create_token(
            user=user,
            token_type=UserToken.TYPE_PASSWORD_RESET,
            hours_valid=PASSWORD_RESET_EXPIRATION_HOURS,
        )

        transaction.on_commit(
            lambda: PasswordResetService._send_reset_email(
                user=user,
                token=token_obj.token,
            )
        )

    @staticmethod
    @transaction.atomic
    def reset_password(*, token: str, new_password: str):
        """
        Reset a user's password using a valid single-use password reset token.
        """

        token_obj = get_valid_token(
            token=token,
            token_type=UserToken.TYPE_PASSWORD_RESET,
        )

        if not token_obj:
            raise TokenInvalidError()

        if token_obj.is_expired():
            token_obj.delete()
            raise TokenExpiredError()

        user = token_obj.user

        try:
            validate_password(new_password, user)
        except DjangoValidationError as exc:
            raise exc

        user.set_password(new_password)
        user.save(update_fields=["password"])

        token_obj.used = True
        token_obj.save(update_fields=["used"])

        return user

    @staticmethod
    def _send_reset_email(*, user, token: str):
        reset_link = (
            settings.SITE_URL
            + reverse("users:password_reset_confirm", kwargs={"token": token})
        )

        subject = "Reset your E-commerce Hub password"

        message = (
            f"Hello {user.user_name},\n\n"
            f"You requested a password reset.\n\n"
            f"Click the link below to set a new password:\n"
            f"{reset_link}\n\n"
            f"This link is valid for {PASSWORD_RESET_EXPIRATION_HOURS} hours.\n\n"
            f"If you did not request this, please ignore this email.\n\n"
            f"E-commerce Hub Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.user_email],
            fail_silently=False,
        )