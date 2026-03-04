from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegisterApi,
    ConfirmEmailApi,
    UserLoginApi,
)

urlpatterns = [
    path("register/", UserRegisterApi.as_view(), name="api-register"),
    path("login/", UserLoginApi.as_view(), name="api-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("confirm-email/<str:token>/", ConfirmEmailApi.as_view(), name="api-confirm-email"),
]