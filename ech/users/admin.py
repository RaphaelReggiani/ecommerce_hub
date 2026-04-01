from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from ech.users.models import CustomUser, UserToken


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser

    list_display = (
        "id",
        "user_email",
        "user_name",
        "user_role",
        "is_active",
        "is_staff",
        "email_confirmed",
        "date_joined",
    )

    list_filter = (
        "user_role",
        "is_active",
        "is_staff",
        "is_superuser",
        "email_confirmed",
        "date_joined",
    )

    search_fields = (
        "user_email",
        "user_name",
        "user_phone",
        "user_country",
        "user_state",
    )

    ordering = ("user_email",)

    readonly_fields = (
        "date_joined",
        "last_login",
    )

    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "user_email",
                    "password",
                )
            },
        ),
        (
            "Profile",
            {
                "fields": (
                    "user_name",
                    "user_role",
                    "user_age",
                    "user_phone",
                    "user_country",
                    "user_state",
                    "user_address",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "email_confirmed",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "user_email",
                    "user_name",
                    "user_role",
                    "password1",
                    "password2",
                    "is_active",
                    "email_confirmed",
                ),
            },
        ),
    )


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "token_type",
        "used",
        "created_at",
        "expires_at",
    )

    list_filter = (
        "token_type",
        "used",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user__user_email",
        "user__user_name",
        "token",
    )

    readonly_fields = (
        "created_at",
    )

    autocomplete_fields = (
        "user",
    )

    ordering = ("-created_at",)
