from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from ech.users.services.password_reset_service import PasswordResetService
from ech.users.exceptions import (
    TokenExpiredError,
    TokenInvalidError,
)

from ech.users.constants.constants import (
    URL_LOGIN,
)

from ech.users.constants.messages import (
    MSG_SUCCESFULL_LOGIN,
)


@require_http_methods(["GET", "POST"])
def password_reset_request_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        PasswordResetService.request_password_reset(email)

        messages.success(
            request,
            "If the email exists, a reset link has been sent."
        )
        return redirect(URL_LOGIN)

    return render(request, "users/password_reset_request.html")


@require_http_methods(["GET", "POST"])
def password_reset_confirm_view(request, token):
    if request.method == "POST":
        password = request.POST.get("password")
        password_confirmation = request.POST.get("password_confirmation")

        if password != password_confirmation:
            messages.error(request, "Passwords do not match.")
            return redirect(request.path)

        try:
            PasswordResetService.reset_password(token, password)
        except TokenExpiredError:
            messages.error(request, "Token expired.")
            return redirect(URL_LOGIN)
        except TokenInvalidError:
            messages.error(request, "Invalid token.")
            return redirect(URL_LOGIN)

        messages.success(request, "Password reset successfully.")
        return redirect(URL_LOGIN)

    return render(
        request,
        "users/password_reset_confirm.html",
        {"token": token},
    )