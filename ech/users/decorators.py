from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib import messages

from ech.users.constants.messages import MSG_ERROR_RESTRICTED_ACCESS


def role_required(*allowed_roles):
    """
    Role-based access control decorator.

    Requires the user to already be authenticated
    (use together with @login_required).
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            if request.user.user_role not in allowed_roles:
                messages.error(request, MSG_ERROR_RESTRICTED_ACCESS)
                return HttpResponseForbidden(MSG_ERROR_RESTRICTED_ACCESS)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator