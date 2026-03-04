from ech.users.constants.messages import (
    MSG_ERROR_USER_ALREADY_EXISTS,
    MSG_ERROR_RESTRICTED_ACCESS,
    MSG_ERROR_TOKEN_EXPIRED,
    MSG_ERROR_INVALID_TOKEN,
    MSG_AUTHENTICATION_FAILED_INACTIVE_ACCOUNT,
)


class UserDomainError(Exception):
    """
    Base exception for all user domain-related errors.

    This exception represents business rule violations
    inside the users domain layer.
    """

    default_message = "User domain error."

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class UserAlreadyExistsError(UserDomainError):
    """
    Raised when attempting to register a user
    with an email that already exists.
    """
    default_message = MSG_ERROR_USER_ALREADY_EXISTS


class InvalidRoleAssignmentError(UserDomainError):
    """
    Raised when an invalid role is assigned
    during user creation or update.
    """
    default_message = MSG_ERROR_INVALID_TOKEN


class InactiveAccountError(UserDomainError):
    """
    Raised when an operation is attempted
    on an inactive account.
    """
    default_message = MSG_AUTHENTICATION_FAILED_INACTIVE_ACCOUNT


class EmailNotConfirmedError(UserDomainError):
    """
    Raised when authentication is attempted
    without email confirmation.
    """
    default_message = MSG_ERROR_RESTRICTED_ACCESS


class TokenError(UserDomainError):
    """
    Base exception for all token-related errors.
    """
    default_message = MSG_ERROR_INVALID_TOKEN


class TokenExpiredError(TokenError):
    """
    Raised when a token is expired.
    """
    default_message = MSG_ERROR_TOKEN_EXPIRED


class TokenInvalidError(TokenError):
    """
    Raised when a token is invalid or malformed.
    """
    default_message = MSG_ERROR_INVALID_TOKEN


class EmailTokenInvalidError(TokenError):
    """
    Raised when an email confirmation token is invalid or malformed.
    """
    default_message = MSG_ERROR_INVALID_TOKEN


class EmailTokenExpiredError(TokenError):
    """
    Raised when an email confirmation token is expired.
    """
    default_message = MSG_ERROR_TOKEN_EXPIRED
