import hashlib
import json
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.urls import reverse

from ech.users.constants.constants import (
    EMAIL_CONFIRMATION_EXPIRATION_HOURS,
)
from ech.users.exceptions import (
    EmailTokenExpiredError,
    EmailTokenInvalidError,
    IdempotencyConflictError,
    UserAlreadyExistsError,
)
from ech.users.models import UserToken
from ech.users.selectors import get_email_confirmation_token

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
        idempotency_key=None,
        **extra_fields,
    ):
        """
        Registers a new user and schedules confirmation email sending.

        If an idempotency key is provided and already associated with an
        existing user, the existing user is returned only when the current
        request payload matches the original request payload.
        """

        if role is None:
            role = User.ROLE_CUSTOMER_USER

        normalized_idempotency_key = (
            UserRegistrationService._normalize_idempotency_key(idempotency_key)
        )

        request_hash = UserRegistrationService._build_registration_request_hash(
            email=email,
            user_name=user_name,
            role=role,
            extra_fields=extra_fields,
        )

        existing_user = UserRegistrationService._get_user_by_idempotency_key(
            normalized_idempotency_key
        )
        if existing_user is not None:
            UserRegistrationService._validate_idempotent_replay(
                user=existing_user,
                request_hash=request_hash,
            )
            return existing_user

        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                role=role,
                user_name=user_name,
                idempotency_key=normalized_idempotency_key,
                idempotency_request_hash=request_hash,
                **extra_fields,
            )
        except IntegrityError:
            if normalized_idempotency_key is not None:
                existing_user = UserRegistrationService._get_user_by_idempotency_key(
                    normalized_idempotency_key
                )
                if existing_user is not None:
                    UserRegistrationService._validate_idempotent_replay(
                        user=existing_user,
                        request_hash=request_hash,
                    )
                    return existing_user

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

    @staticmethod
    def _get_user_by_idempotency_key(idempotency_key):
        if idempotency_key is None:
            return None

        return User.objects.filter(idempotency_key=idempotency_key).first()

    @staticmethod
    def _normalize_idempotency_key(idempotency_key):
        if not idempotency_key:
            return None

        if isinstance(idempotency_key, uuid.UUID):
            return idempotency_key

        try:
            return uuid.UUID(str(idempotency_key))
        except (TypeError, ValueError, AttributeError):
            return None

    @staticmethod
    def _build_registration_request_hash(
        *,
        email: str,
        user_name: str,
        role: str,
        extra_fields: dict,
    ):
        normalized_payload = {
            "email": (email or "").strip().lower(),
            "user_name": user_name,
            "role": role,
            "extra_fields": extra_fields or {},
        }

        payload_json = json.dumps(
            normalized_payload,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )

        return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate_idempotent_replay(*, user, request_hash: str):
        stored_hash = getattr(user, "idempotency_request_hash", None)

        if stored_hash and stored_hash != request_hash:
            raise IdempotencyConflictError()