from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction, IntegrityError
from django.urls import reverse

from ech.users.models import UserToken
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
    def register_user(form):
        """
        Receives a validated form and registers a user.
        Sends confirmation email.
        """

        user = form.save(commit=False)
        user.is_active = False
        user.email_confirmed = False

        try:
            user.save()
        except IntegrityError:
            raise UserAlreadyExistsError()

        token = UserRegistrationService._generate_email_token(user)
        UserRegistrationService._send_confirmation_email(user, token)

        return user

    @staticmethod
    def confirm_email(token):

        try:
            token_obj = UserToken.objects.select_related("user").get(
                token=token,
                token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            )
        except UserToken.DoesNotExist:
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
            f"This link is valid for 24 hours.\n\n"
            f"E-commerce Hub Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.user_email],
            fail_silently=False,
        )