from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        """
        Rate limit login attempts per IP address.
        """

        ip = self.get_ident(request)

        if not ip:
            return None

        return f"login_rate_{ip}"