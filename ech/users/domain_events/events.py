class BaseDomainEvent:
    """
    Base domain event.
    """

    event_name = "base_domain_event"

    def to_dict(self):
        """
        Serialize event payload for logging, debugging, or handlers.
        """

        return self.__dict__.copy()


class UserRegisteredEvent(BaseDomainEvent):
    """
    Event triggered when a user is registered.
    """

    event_name = "user_registered"

    def __init__(
        self,
        *,
        user_id,
        email,
        role,
        performed_by_id=None,
        ip_address=None,
        user_agent=None,
        request_id=None,
    ):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.performed_by_id = performed_by_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.request_id = request_id


class UserEmailConfirmedEvent(BaseDomainEvent):
    """
    Event triggered when a user confirms their email.
    """

    event_name = "user_email_confirmed"

    def __init__(
        self,
        *,
        user_id,
        email,
        performed_by_id=None,
        ip_address=None,
        user_agent=None,
        request_id=None,
    ):
        self.user_id = user_id
        self.email = email
        self.performed_by_id = performed_by_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.request_id = request_id


class UserPasswordResetRequestedEvent(BaseDomainEvent):
    """
    Event triggered when a password reset is requested.
    """

    event_name = "user_password_reset_requested"

    def __init__(
        self,
        *,
        user_id,
        email,
        performed_by_id=None,
        ip_address=None,
        user_agent=None,
        request_id=None,
    ):
        self.user_id = user_id
        self.email = email
        self.performed_by_id = performed_by_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.request_id = request_id


class UserPasswordChangedEvent(BaseDomainEvent):
    """
    Event triggered when a user's password is changed.
    """

    event_name = "user_password_changed"

    def __init__(
        self,
        *,
        user_id,
        performed_by_id=None,
        ip_address=None,
        user_agent=None,
        request_id=None,
    ):
        self.user_id = user_id
        self.performed_by_id = performed_by_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.request_id = request_id


class UserLoginSucceededEvent(BaseDomainEvent):
    """
    Event triggered when a user login succeeds.
    """

    event_name = "user_login_succeeded"

    def __init__(
        self,
        *,
        user_id,
        email,
        ip_address=None,
        user_agent=None,
        request_id=None,
    ):
        self.user_id = user_id
        self.email = email
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.request_id = request_id


class UserLoginFailedEvent(BaseDomainEvent):
    """
    Event triggered when a user login fails.
    """

    event_name = "user_login_failed"

    def __init__(
        self,
        *,
        email,
        ip_address=None,
        user_agent=None,
        request_id=None,
    ):
        self.email = email
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.request_id = request_id


class UserTokenInvalidEvent(BaseDomainEvent):
    """
    Event triggered when an invalid or expired token is used.
    """

    event_name = "user_token_invalid"

    def __init__(
        self,
        *,
        token_type,
        ip_address=None,
        user_agent=None,
        request_id=None,
    ):
        self.token_type = token_type
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.request_id = request_id