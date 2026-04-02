from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """
    Rate limit login attempts per client IP.
    """

    scope = "login"

    def get_cache_key(self, request, view):
        ip_address = self.get_ident(request)

        if not ip_address:
            return None

        return f"login_rate_{ip_address}"