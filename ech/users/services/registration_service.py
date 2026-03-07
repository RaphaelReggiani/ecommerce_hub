from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction, IntegrityError
from django.urls import reverse

from ech.users.models import UserToken
from ech.users.selectors import get_email_confirmation_token
from ech.users.exceptions import (
    UserAlreadyExistsError,
    EmailTokenInvalidError,
    EmailTokenExpiredError,
)

from ech.users.constants.constants import (
    EMAIL_CONFIRMATION_EXPIRATION_HOURS,
)

User = get_user_model()


class UserRegistrationService:
    """
    Handles user registration and email confirmation logic.
    """

    @staticmethod
    @transaction.atomic
    def register_user(
        *,
        email: str,
        password: str,
        user_name: str,
        role: str = None,
        **extra_fields,
    ):
        """
        Registers a new user and schedules confirmation email sending.
        """

        if role is None:
            role = User.ROLE_CUSTOMER_USER

        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                role=role,
                user_name=user_name,
                **extra_fields,
            )
        except IntegrityError:
            raise UserAlreadyExistsError()

        user.is_active = False
        user.email_confirmed = False
        user.save(update_fields=["is_active", "email_confirmed"])

        token = UserRegistrationService._generate_email_token(user)

        transaction.on_commit(
            lambda: UserRegistrationService._send_confirmation_email(user, token)
        )

        return user

    @staticmethod
    def confirm_email(token: str):

        token_obj = get_email_confirmation_token(token)

        if not token_obj:
            raise EmailTokenInvalidError()

        if token_obj.is_expired():
            token_obj.delete()
            raise EmailTokenExpiredError()

        user = token_obj.user
        user.is_active = True
        user.email_confirmed = True
        user.save(update_fields=["is_active", "email_confirmed"])

        token_obj.delete()

        return user

    @staticmethod
    def _generate_email_token(user):

        UserToken.objects.filter(
            user=user,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
        ).delete()

        token_obj = UserToken.create_token(
            user=user,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            hours_valid=EMAIL_CONFIRMATION_EXPIRATION_HOURS,
        )

        return token_obj.token

    @staticmethod
    def _send_confirmation_email(user, token):

        confirmation_link = (
            settings.SITE_URL
            + reverse("users:confirm_email", kwargs={"token": token})
        )

        subject = "Confirm your E-commerce Hub account"

        message = (
            f"Hello {user.user_name},\n\n"
            f"Please confirm your account by clicking the link below:\n"
            f"{confirmation_link}\n\n"
            f"This link is valid for {EMAIL_CONFIRMATION_EXPIRATION_HOURS} hours.\n\n"
            f"E-commerce Hub Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.user_email],
            fail_silently=False,
        )