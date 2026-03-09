from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ech.users.decorators import role_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from ech.users.exceptions import (
    TokenExpiredError,
    TokenInvalidError,
)

from ech.users.constants.constants import (
    URL_HOME,
    URL_LOGIN,
    URL_CUSTOMER_PROFILE,
)

from ech.users.constants.messages import (
    MSG_SUCCESFULL_REGISTRATION,
    MSG_SUCCESFULL_LOGIN,
    MSG_SUCCESFULL_LOGOUT,
    MSG_SUCCESFULL_PROFILE_UPDATE,
    MSG_SUCCESFULL_USER_CREATED,
    MSG_AUTHENTICATION_FAILED_EMAIL_PASSWORD,
    MSG_AUTHENTICATION_FAILED_INACTIVE_ACCOUNT,
    MSG_INVALID_ROLE_ASSIGNMENT_NOT_SUPERADMIN,
    MSG_ERROR_HTTP404_INVALID_TOKEN,
    MSG_ERROR_HTTP404_EXPIRED_TOKEN,
)

from ech_web.users.forms.forms import (
    CustomerUserRegistrationForm,
    StaffUserCreationForm,
    UserProfileUpdateForm,
)

from ech.users.models import CustomUser
from ech.users.services.registration_service import UserRegistrationService


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password,
        )

        if user is None:
            messages.error(request, MSG_AUTHENTICATION_FAILED_EMAIL_PASSWORD)
            return redirect(URL_LOGIN)

        if not user.is_active:
            messages.error(request, MSG_AUTHENTICATION_FAILED_INACTIVE_ACCOUNT)
            return redirect(URL_LOGIN)

        login(request, user)
        messages.success(request, MSG_SUCCESFULL_LOGIN)
        return redirect(URL_HOME)

    return render(request, "users/login.html")


@login_required(login_url=URL_LOGIN)
def logout_view(request):
    logout(request)
    messages.success(request, MSG_SUCCESFULL_LOGOUT)
    return redirect(URL_LOGIN)


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "POST":
        form = CustomerUserRegistrationForm(request.POST)

        if form.is_valid():
            UserRegistrationService.register_user(form)
            messages.success(request, MSG_SUCCESFULL_REGISTRATION)
            return redirect(URL_LOGIN)
    else:
        form = CustomerUserRegistrationForm()

    return render(request, "users/register.html", {"form": form})


@require_http_methods(["GET"])
def confirm_email_view(request, token):
    try:
        UserRegistrationService.confirm_email(token)
    except TokenInvalidError:
        raise Http404(MSG_ERROR_HTTP404_INVALID_TOKEN)

    except TokenExpiredError:
        raise Http404(MSG_ERROR_HTTP404_EXPIRED_TOKEN)

    return render(request, "users/email_confirmed.html")


@require_http_methods(["GET", "POST"])
@login_required(login_url=URL_LOGIN)
def user_profile_view(request):

    if request.method == "POST":
        form = UserProfileUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, MSG_SUCCESFULL_PROFILE_UPDATE)
            return redirect(URL_CUSTOMER_PROFILE)

    else:
        form = UserProfileUpdateForm(instance=request.user)

    return render(request, "users/profile.html", {"form": form})


@require_http_methods(["GET", "POST"])
@login_required(login_url=URL_LOGIN)
@role_required(CustomUser.ROLE_ADMIN)
def create_staff_user_view(request):

    if request.method == "POST":
        form = StaffUserCreationForm(request.POST)

        if form.is_valid():

            selected_role = form.cleaned_data["user_role"]

            if selected_role == CustomUser.ROLE_ADMIN:
                raise PermissionDenied(MSG_INVALID_ROLE_ASSIGNMENT_NOT_SUPERADMIN)

            UserRegistrationService.register_user(form)
            messages.success(request, MSG_SUCCESFULL_USER_CREATED)
            return redirect(URL_HOME)

    else:
        form = StaffUserCreationForm()

    return render(
        request,
        "users/create_staff_user.html",
        {"form": form},
    )


@login_required(login_url=URL_LOGIN)
@role_required(CustomUser.ROLE_CUSTOMER_USER)
def customer_dashboard(request):
    return render(request, "users/customer.html")


@login_required(login_url=URL_LOGIN)
@role_required(CustomUser.ROLE_SUPPORT_STAFF)
def support_staff_dashboard(request):
    return render(request, "users/support_staff.html")


@login_required(login_url=URL_LOGIN)
@role_required(CustomUser.ROLE_PAYMENT_STAFF)
def payment_staff_dashboard(request):
    return render(request, "users/payment_staff.html")


@login_required(login_url=URL_LOGIN)
@role_required(CustomUser.ROLE_OPERATIONS_STAFF)
def operations_staff_dashboard(request):
    return render(request, "users/operations_staff.html")


@login_required(login_url=URL_LOGIN)
@role_required(CustomUser.ROLE_ADMIN)
def adm_dashboard(request):
    return render(request, "users/adm.html")