from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

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
    LABEL_SUPERADM,
    LABEL_SUPER_STAFF,
    LABEL_PAYMENT_STAFF,
    LABEL_PROCCESS_STAFF,
    LABEL_SUPPORT_STAFF,
    LABEL_COMMON_USER,
)

from ech.users.constants.messages import (
    MSG_VALUE_ERROR_INFORM_EMAIL,
    MSG_VALUE_ERROR_INFORM_PASSWORD,
    MSG_VALIDATION_ERROR_STAFF_EMAIL,
)


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError(MSG_VALUE_ERROR_INFORM_EMAIL)

        if not password:
            raise ValueError(MSG_VALUE_ERROR_INFORM_PASSWORD)

        email = self.normalize_email(email).lower()

        if role is None:
            role = CustomUser.ROLE_COMMON_USER

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
            role=CustomUser.ROLE_SUPERADM,
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

    ROLE_SUPERADM = "superadm"
    ROLE_SUPER_STAFF = "super_staff"
    ROLE_PAYMENT_STAFF = "payment_staff"
    ROLE_PROCCESS_STAFF = "proccess_staff"
    ROLE_SUPPORT_STAFF = "support_staff"
    ROLE_COMMON_USER = "common_user"

    ROLE_CHOICES = [
        (ROLE_COMMON_USER, LABEL_COMMON_USER),
        (ROLE_SUPPORT_STAFF, LABEL_SUPPORT_STAFF),
        (ROLE_PROCCESS_STAFF, LABEL_PROCCESS_STAFF),
        (ROLE_PAYMENT_STAFF, LABEL_PAYMENT_STAFF),
        (ROLE_SUPER_STAFF, LABEL_SUPER_STAFF),
        (ROLE_SUPERADM, LABEL_SUPERADM),
    ]


    user_name = models.CharField(max_length=MAX_LENGTH_NAME)
    user_email = models.EmailField(unique=True)
    user_role = models.CharField(
        max_length=MAX_LENGTH_ROLE,
        choices=ROLE_CHOICES,
        default=ROLE_COMMON_USER,
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

    def clean(self):

        if self.user_role != self.ROLE_COMMON_USER:
            if not self.user_email.endswith(CORPORATE_EMAIL_DOMAIN):
                raise ValidationError(MSG_VALIDATION_ERROR_STAFF_EMAIL)

    @property
    def is_superadm(self):
        return self.user_role == self.ROLE_SUPERADM

    @property
    def can_create_staff(self):
        return self.user_role in {
            self.ROLE_SUPERADM,
            self.ROLE_SUPER_STAFF,
        }

    def save(self, *args, **kwargs):

        if self.user_email:
            self.user_email = self.user_email.lower()

        if self.user_role == self.ROLE_SUPERADM:
            self.is_staff = True
            self.is_superuser = True
        elif self.user_role == self.ROLE_SUPER_STAFF:
            self.is_staff = True
            self.is_superuser = False
        else:
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_name} ({self.user_email})"