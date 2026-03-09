from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from ech.users.services.password_reset_service import PasswordResetService
from ech.users.exceptions import (
    TokenExpiredError,
    TokenInvalidError,
)

from ech.users.constants.constants import (
    URL_LOGIN,
    URL_HOME,
)

from ech.users.constants.messages import (
    MSG_SUCCESFULL_RESET_LINK_SENT,
    MSG_SUCCESFULL_PASSWORD_RESET,
    MSG_ERROR_PASSWORDS_DO_NOT_MATCH,
    MSG_ERROR_TOKEN_EXPIRED,
    MSG_ERROR_INVALID_TOKEN,
)


@require_http_methods(["GET", "POST"])
def password_reset_request_view(request):

    if request.user.is_authenticated:
        return redirect(URL_HOME)

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        PasswordResetService.request_password_reset(email)

        messages.success(request, MSG_SUCCESFULL_RESET_LINK_SENT)
        return redirect(URL_LOGIN)

    return render(request, "users/password_reset_request.html")


@require_http_methods(["GET", "POST"])
def password_reset_confirm_view(request, token):

    try:
        PasswordResetService.validate_token(token)

    except TokenExpiredError:
        messages.error(request, MSG_ERROR_TOKEN_EXPIRED)
        return redirect(URL_LOGIN)

    except TokenInvalidError:
        messages.error(request, MSG_ERROR_INVALID_TOKEN)
        return redirect(URL_LOGIN)

    if request.method == "POST":

        password = request.POST.get("password", "")
        password_confirmation = request.POST.get("password_confirmation", "")

        if password != password_confirmation:
            messages.error(request, MSG_ERROR_PASSWORDS_DO_NOT_MATCH)
            return redirect("password_reset_confirm", token=token)

        try:
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect("password_reset_confirm", token=token)

        try:
            PasswordResetService.reset_password(token, password)

        except TokenExpiredError:
            messages.error(request, MSG_ERROR_TOKEN_EXPIRED)
            return redirect(URL_LOGIN)

        except TokenInvalidError:
            messages.error(request, MSG_ERROR_INVALID_TOKEN)
            return redirect(URL_LOGIN)

        messages.success(request, MSG_SUCCESFULL_PASSWORD_RESET)
        return redirect(URL_LOGIN)

    return render(
        request,
        "users/password_reset_confirm.html",
        {"token": token},
    )