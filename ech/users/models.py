from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
from django.conf import settings

from ech.users.constants.constants import (
    MAX_LENGTH_NAME,
    MAX_LENGTH_PHONE,
    MINIMUM_AGE,
    MAXIMUM_AGE,
    CORPORATE_EMAIL_DOMAIN,
    MAX_LENGTH_ROLE,
    MAX_LENGTH_ADDRESS,
    MAX_LENGTH_COUNTRY,
    MAX_LENGTH_STATE,
    LABEL_SUPERADMIN,
    LABEL_ADMIN,
    LABEL_PAYMENT_STAFF,
    LABEL_OPERATIONS_STAFF,
    LABEL_SUPPORT_STAFF,
    LABEL_CUSTOMER_USER,
    LABEL_TOKEN_TYPE_EMAIL_CONFIRMATION,
    LABEL_TOKEN_TYPE_PASSWORD_RESET,
    LABEL_TOKEN_TYPE_MAGIC_LOGIN,
    LABEL_TOKEN_TYPE_INVITATION,
    LABEL_TOKEN_TYPE_EMAIL_CHANGE,
    LABEL_TOKEN_TYPE_2FA,
)

from ech.users.constants.messages import (
    MSG_VALUE_ERROR_INFORM_EMAIL,
    MSG_VALUE_ERROR_INFORM_PASSWORD,
    MSG_VALIDATION_ERROR_STAFF_EMAIL,
    MSG_VALIDATION_ERROR_EXPIRATION_DATETIME,
)


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError(MSG_VALUE_ERROR_INFORM_EMAIL)

        if not password:
            raise ValueError(MSG_VALUE_ERROR_INFORM_PASSWORD)

        email = self.normalize_email(email).lower()

        if role is None:
            role = CustomUser.ROLE_CUSTOMER_USER

        user = self.model(
            user_email=email,
            user_role=role,
            **extra_fields,
        )

        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(
            email=email,
            password=password,
            role=CustomUser.ROLE_SUPERADMIN,
            **extra_fields,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.email_confirmed = True
        user.save(update_fields=[
            "is_staff",
            "is_superuser",
            "is_active",
            "email_confirmed",
        ])
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):

    ROLE_SUPERADMIN = "superadmin"
    ROLE_ADMIN = "admin"
    ROLE_PAYMENT_STAFF = "payment_staff"
    ROLE_OPERATIONS_STAFF = "operations_staff"
    ROLE_SUPPORT_STAFF = "support_staff"
    ROLE_CUSTOMER_USER = "customer_user"

    ROLE_CHOICES = [
        (ROLE_CUSTOMER_USER, LABEL_CUSTOMER_USER),
        (ROLE_SUPPORT_STAFF, LABEL_SUPPORT_STAFF),
        (ROLE_OPERATIONS_STAFF, LABEL_OPERATIONS_STAFF),
        (ROLE_PAYMENT_STAFF, LABEL_PAYMENT_STAFF),
        (ROLE_ADMIN, LABEL_ADMIN),
        (ROLE_SUPERADMIN, LABEL_SUPERADMIN),
    ]


    user_name = models.CharField(max_length=MAX_LENGTH_NAME)
    user_email = models.EmailField(unique=True)
    user_role = models.CharField(
        max_length=MAX_LENGTH_ROLE,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER_USER,
        db_index=True,
    )

    user_age = models.PositiveIntegerField(
        validators=[
            MinValueValidator(MINIMUM_AGE),
            MaxValueValidator(MAXIMUM_AGE),
        ],
        blank=True,
        null=True,
    )

    user_phone = models.CharField(max_length=MAX_LENGTH_PHONE, blank=True)
    user_country = models.CharField(max_length=MAX_LENGTH_COUNTRY, blank=True)
    user_state = models.CharField(max_length=MAX_LENGTH_STATE, blank=True)
    user_address = models.CharField(max_length=MAX_LENGTH_ADDRESS, blank=True)


    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "user_email"
    REQUIRED_FIELDS = ["user_name"]

    objects = CustomUserManager()

    class Meta:
        indexes = [
            models.Index(fields=["user_email"]),
            models.Index(fields=["user_role"]),
        ]

    def clean(self):
        super().clean()

        if self.user_role != self.ROLE_CUSTOMER_USER:
            email_domain = self.user_email.split("@")[-1]
            corporate_domain = CORPORATE_EMAIL_DOMAIN.lstrip("@")

            if email_domain != corporate_domain:
                raise ValidationError(MSG_VALIDATION_ERROR_STAFF_EMAIL)
            
    @property
    def is_superadmin(self):
        return self.user_role == self.ROLE_SUPERADMIN

    @property
    def can_create_staff(self):
        return self.user_role in {
            self.ROLE_SUPERADMIN,
            self.ROLE_ADMIN,
        }

    def save(self, *args, **kwargs):

        if self.user_email:
            self.user_email = self.user_email.lower()

        if self.user_role == self.ROLE_SUPERADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.user_role == self.ROLE_ADMIN:
            self.is_staff = True
            self.is_superuser = False
        else:
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_name} ({self.user_email})"
    

class UserToken(models.Model):

    TYPE_EMAIL_CONFIRMATION = "email_confirmation"
    TYPE_PASSWORD_RESET = "password_reset"
    TYPE_MAGIC_LOGIN = "magic_login"
    TYPE_INVITATION = "invitation"
    TYPE_EMAIL_CHANGE = "email_change"
    TYPE_2FA = "two_factor"

    TOKEN_TYPE_CHOICES = [
        (TYPE_EMAIL_CONFIRMATION, LABEL_TOKEN_TYPE_EMAIL_CONFIRMATION),
        (TYPE_PASSWORD_RESET, LABEL_TOKEN_TYPE_PASSWORD_RESET),
        (TYPE_MAGIC_LOGIN, LABEL_TOKEN_TYPE_MAGIC_LOGIN),
        (TYPE_INVITATION, LABEL_TOKEN_TYPE_INVITATION),
        (TYPE_EMAIL_CHANGE, LABEL_TOKEN_TYPE_EMAIL_CHANGE),
        (TYPE_2FA, LABEL_TOKEN_TYPE_2FA),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tokens",
    )

    token = models.CharField(max_length=128, unique=True)

    token_type = models.CharField(
        max_length=32,
        choices=TOKEN_TYPE_CHOICES,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    used = models.BooleanField(default=False)

    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "user_tokens"
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["token_type"]),
            models.Index(fields=["user", "token_type"]),
        ]

    def clean(self):
        super().clean()

        if self.expires_at <= timezone.now():
            raise ValidationError(MSG_VALIDATION_ERROR_EXPIRATION_DATETIME)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def mark_as_used(self):
        self.used = True
        self.save(update_fields=["used"])

    @classmethod
    def create_token(cls, *, user, token_type, hours_valid):
        return cls.objects.create(
            user=user,
            token=get_random_string(48),
            token_type=token_type,
            expires_at=timezone.now() + timedelta(hours=hours_valid),
        )