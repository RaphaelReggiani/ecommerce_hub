class UserDomainError(Exception):
    """Base exception for user domain."""


class UserAlreadyExistsError(UserDomainError):
    pass


class EmailTokenInvalidError(UserDomainError):
    pass


class EmailTokenExpiredError(UserDomainError):
    pass


class InvalidRoleAssignment(UserDomainError):
    pass


class InactiveAccountError(UserDomainError):
    pass


class EmailNotConfirmedError(UserDomainError):
    pass


class TokenError(UserDomainError):
    """Base exception for token-related errors."""


class TokenExpiredError(TokenError):
    pass


class TokenInvalidError(TokenError):
    pass