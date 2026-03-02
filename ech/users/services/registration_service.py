from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.urls import reverse

from ech.users.constants.messages import (
    MSG_ERROR_USER_ALREADY_EXISTS,
    MSG_AUTHENTICATION_FAILED_INACTIVE_ACCOUNT,
)

User = get_user_model()

class EmailConfirmationToken(models.Model):
    """
    Token temporário para confirmação de e-mail.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="email_confirmation_token",
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "email_confirmation_tokens"

    def is_expired(self):
        expiration_time = self.created_at + timezone.timedelta(hours=24)
        return timezone.now() > expiration_time


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

        if User.objects.filter(user_email=user.user_email).exists():
            raise ValueError(MSG_ERROR_USER_ALREADY_EXISTS)

        user.is_active = False
        user.email_confirmed = False
        user.save()

        token = UserRegistrationService._generate_email_token(user)

        UserRegistrationService._send_confirmation_email(user, token)

        return user

    @staticmethod
    def confirm_email(token):
        """
        Confirms user email using token.
        """
        try:
            token_obj = EmailConfirmationToken.objects.select_related("user").get(
                token=token
            )
        except EmailConfirmationToken.DoesNotExist:
            raise ValueError("Invalid or expired token.")

        if token_obj.is_expired():
            token_obj.delete()
            raise ValueError("Token expired.")

        user = token_obj.user
        user.is_active = True
        user.email_confirmed = True
        user.save(update_fields=["is_active", "email_confirmed"])

        token_obj.delete()

        return user

    @staticmethod
    def _generate_email_token(user):
        token = get_random_string(48)

        EmailConfirmationToken.objects.update_or_create(
            user=user,
            defaults={"token": token},
        )

        return token

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