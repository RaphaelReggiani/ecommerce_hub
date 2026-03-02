from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from ech.users.constants.constants import (
    URL_HOME,
    URL_LOGIN,
    URL_LOGOUT,
    URL_REGISTER,
    URL_USER_PROFILE,
    URL_SUPER_STAFF,
    URL_PAYMENT_STAFF,
    URL_PROCCESS_STAFF,
    URL_SUPPORT_STAFF,
)

from ech.users.constants.messages import (
    MSG_SUCCESFULL_REGISTRATION,
    MSG_SUCCESFULL_LOGIN,
    MSG_SUCCESFULL_LOGOUT,
    MSG_SUCCESFULL_PROFILE_UPDATE,
    MSG_SUCCESFULL_USER_CREATED,
    MSG_ERROR_RESTRICTED_ACCESS,
    MSG_ERROR_NO_USER_LOGGED,
    MSG_AUTHENTICATION_FAILED_EMAIL_PASSWORD,
    MSG_AUTHENTICATION_FAILED_INACTIVE_ACCOUNT,
)

from ech.users.forms import (
    CommonUserRegistrationForm,
    StaffUserCreationForm,
)

from ech.users.models import CustomUser
from ech.users.services.registration_service import UserRegistrationService


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
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
        form = CommonUserRegistrationForm(request.POST)

        if form.is_valid():
            UserRegistrationService.register_user(form)
            messages.success(request, MSG_SUCCESFULL_REGISTRATION)
            return redirect(URL_LOGIN)

    else:
        form = CommonUserRegistrationForm()

    return render(request, "users/register.html", {"form": form})


def confirm_email_view(request, token):
    try:
        UserRegistrationService.confirm_email(token)
    except ValueError:
        raise Http404("Invalid or expired token.")

    return render(request, "users/email_confirmed.html")


@login_required(login_url=URL_LOGIN)
@require_http_methods(["GET", "POST"])
def user_profile_view(request):
    user = request.user

    if request.method == "POST":
        user.user_name = request.POST.get("user_name", user.user_name)
        user.user_phone = request.POST.get("user_phone", user.user_phone)
        user.user_country = request.POST.get("user_country", user.user_country)
        user.user_state = request.POST.get("user_state", user.user_state)
        user.user_address = request.POST.get("user_address", user.user_address)

        user.save()
        messages.success(request, MSG_SUCCESFULL_PROFILE_UPDATE)
        return redirect(URL_USER_PROFILE)

    return render(request, "users/profile.html", {"user": user})


@login_required(login_url=URL_LOGIN)
@require_http_methods(["GET", "POST"])
def create_staff_user_view(request):
    request_user = request.user

    if not request_user.can_create_staff:
        return HttpResponseForbidden(MSG_ERROR_RESTRICTED_ACCESS)

    if request.method == "POST":
        form = StaffUserCreationForm(
            request.POST,
            request_user=request_user,
        )

        if form.is_valid():
            UserRegistrationService.register_user(form)
            messages.success(request, MSG_SUCCESFULL_USER_CREATED)
            return redirect(URL_HOME)

    else:
        form = StaffUserCreationForm(request_user=request_user)

    return render(
        request,
        "users/create_staff_user.html",
        {"form": form},
    )


@login_required(login_url=URL_LOGIN)
def support_staff_dashboard(request):
    if request.user.user_role != CustomUser.ROLE_SUPPORT_STAFF:
        return HttpResponseForbidden(MSG_ERROR_RESTRICTED_ACCESS)
    return render(request, "users/support_staff.html")


@login_required(login_url=URL_LOGIN)
def payment_staff_dashboard(request):
    if request.user.user_role != CustomUser.ROLE_PAYMENT_STAFF:
        return HttpResponseForbidden(MSG_ERROR_RESTRICTED_ACCESS)
    return render(request, "users/payment_staff.html")


@login_required(login_url=URL_LOGIN)
def proccess_staff_dashboard(request):
    if request.user.user_role != CustomUser.ROLE_PROCCESS_STAFF:
        return HttpResponseForbidden(MSG_ERROR_RESTRICTED_ACCESS)
    return render(request, "users/proccess_staff.html")


@login_required(login_url=URL_LOGIN)
def super_staff_dashboard(request):
    if request.user.user_role != CustomUser.ROLE_SUPER_STAFF:
        return HttpResponseForbidden(MSG_ERROR_RESTRICTED_ACCESS)
    return render(request, "users/super_staff.html")