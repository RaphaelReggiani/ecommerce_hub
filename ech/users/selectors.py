from django.contrib.auth import get_user_model
from django.utils import timezone

from ech.users.models import UserToken

User = get_user_model()


def get_user_by_id(user_id: int):
    return User.objects.filter(id=user_id).first()


def get_user_by_email(email: str):
    return User.objects.filter(user_email=email.lower()).first()


def list_users_by_role(role: str):
    return User.objects.filter(user_role=role)


def list_active_users():
    return User.objects.filter(is_active=True)


def list_staff_users():
    return User.objects.filter(is_staff=True)


def get_email_confirmation_token(token: str):
    return (
        UserToken.objects
        .select_related("user")
        .filter(
            token=token,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            used=False,
        )
        .first()
    )


def get_valid_token(token: str, token_type: str):
    return (
        UserToken.objects
        .select_related("user")
        .filter(
            token=token,
            token_type=token_type,
            used=False,
            expires_at__gt=timezone.now(),
        )
        .first()
    )