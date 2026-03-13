def get_client_ip(request):
    """
    Extract client IP address from request.
    """

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    return ip


def get_user_agent(request):
    """
    Extract user agent from request.
    """

    return request.META.get("HTTP_USER_AGENT", "")


def get_request_id(request):
    """
    Retrieve request id if request middleware defines one.
    """

    return getattr(request, "request_id", None)