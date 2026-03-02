from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models, transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.urls import reverse

from ech.users.exceptions import (
    TokenExpiredError,
    TokenInvalidError,
)

User = get_user_model()


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    class Meta:
        db_table = "password_reset_tokens"

    def is_expired(self):
        expiration_time = self.created_at + timezone.timedelta(hours=2)
        return timezone.now() > expiration_time


class PasswordResetService:

    @staticmethod
    def request_password_reset(email):
        """
        Always return success to avoid user enumeration.
        """
        try:
            user = User.objects.get(user_email=email)
        except User.DoesNotExist:
            return

        if not user.is_active:
            return

        token = get_random_string(48)

        PasswordResetToken.objects.create(
            user=user,
            token=token,
        )

        PasswordResetService._send_reset_email(user, token)

    @staticmethod
    @transaction.atomic
    def reset_password(token, new_password):
        try:
            token_obj = PasswordResetToken.objects.select_related("user").get(
                token=token,
                used=False,
            )
        except PasswordResetToken.DoesNotExist:
            raise TokenInvalidError("Invalid token.")

        if token_obj.is_expired():
            token_obj.delete()
            raise TokenExpiredError("Token expired.")

        user = token_obj.user
        user.set_password(new_password)
        user.save(update_fields=["password"])

        token_obj.used = True
        token_obj.save(update_fields=["used"])

        return user

    @staticmethod
    def _send_reset_email(user, token):
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
            f"This link is valid for 2 hours.\n\n"
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