from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ConfirmEmailApi,
    CurrentUserApi,
    PasswordResetConfirmApi,
    PasswordResetRequestApi,
    UserLoginApi,
    UserLogoutApi,
    UserProfileApi,
    UserRegisterApi,
)

app_name = "users-api"

urlpatterns = [

    path("register/", UserRegisterApi.as_view(), name="api-register"),
    path("login/", UserLoginApi.as_view(), name="api-login"),
    path("logout/", UserLogoutApi.as_view(), name="api-logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),

    path(
        "confirm-email/<str:token>/",
        ConfirmEmailApi.as_view(),
        name="api-confirm-email",
    ),

    path(
        "password-reset/",
        PasswordResetRequestApi.as_view(),
        name="api-password-reset",
    ),
    path(
        "password-reset-confirm/",
        PasswordResetConfirmApi.as_view(),
        name="api-password-reset-confirm",
    ),

    path(
        "profile/",
        UserProfileApi.as_view(),
        name="api-profile",
    ),
    path(
        "me/",
        CurrentUserApi.as_view(),
        name="api-me",
    ),
]