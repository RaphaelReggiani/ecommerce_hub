from django.http import HttpResponse
from django.urls import path

app_name = "users"


def placeholder_view(request, *args, **kwargs):
    return HttpResponse("OK")


urlpatterns = [
    path(
        "confirm-email/<str:token>/",
        placeholder_view,
        name="confirm_email",
    ),
    path(
        "password-reset-confirm/<str:token>/",
        placeholder_view,
        name="password_reset_confirm",
    ),
]