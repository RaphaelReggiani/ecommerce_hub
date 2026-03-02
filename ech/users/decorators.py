from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages

from ech.users.constants.constants import URL_LOGIN
from ech.users.constants.messages import MSG_ERROR_RESTRICTED_ACCESS


def role_required(*allowed_roles):
    """
    Generic role-based access decorator.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect(URL_LOGIN)

            if user.user_role not in allowed_roles:
                messages.error(request, MSG_ERROR_RESTRICTED_ACCESS)
                return HttpResponseForbidden(MSG_ERROR_RESTRICTED_ACCESS)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def staff_required(view_func):
    """
    Shortcut for any staff user.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(URL_LOGIN)

        if not request.user.is_staff:
            messages.error(request, MSG_ERROR_RESTRICTED_ACCESS)
            return HttpResponseForbidden(MSG_ERROR_RESTRICTED_ACCESS)

        return view_func(request, *args, **kwargs)

    return _wrapped_view