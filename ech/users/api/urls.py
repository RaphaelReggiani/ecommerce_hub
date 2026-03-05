from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegisterApi,
    ConfirmEmailApi,
    UserLoginApi,
    UserLogoutApi,
    UserProfileApi,
)

app_name = "users"

urlpatterns = [
    path("register/", UserRegisterApi.as_view(), name="api-register"),
    path("login/", UserLoginApi.as_view(), name="api-login"),
    path("logout/", UserLogoutApi.as_view(), name="api-logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("confirm-email/<str:token>/", ConfirmEmailApi.as_view(), name="api-confirm-email"),
    path("profile/", UserProfileApi.as_view(), name="api-profile"),
]