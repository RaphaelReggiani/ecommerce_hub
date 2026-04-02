from ech.users.domain_events.events import (
    UserRegisteredEvent,
    UserEmailConfirmedEvent,
    UserPasswordResetRequestedEvent,
    UserPasswordChangedEvent,
    UserLoginSucceededEvent,
    UserLoginFailedEvent,
    UserTokenInvalidEvent,
)

from ech.users.domain_events.handlers import (
    handle_user_registered,
    handle_user_email_confirmed,
    handle_user_password_reset_requested,
    handle_user_password_changed,
    handle_user_login_succeeded,
    handle_user_login_failed,
    handle_user_token_invalid,
)


EVENT_HANDLER_REGISTRY = {
    UserRegisteredEvent: [
        handle_user_registered,
    ],
    UserEmailConfirmedEvent: [
        handle_user_email_confirmed,
    ],
    UserPasswordResetRequestedEvent: [
        handle_user_password_reset_requested,
    ],
    UserPasswordChangedEvent: [
        handle_user_password_changed,
    ],
    UserLoginSucceededEvent: [
        handle_user_login_succeeded,
    ],
    UserLoginFailedEvent: [
        handle_user_login_failed,
    ],
    UserTokenInvalidEvent: [
        handle_user_token_invalid,
    ],
}