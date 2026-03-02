class UserDomainError(Exception):
    """Base exception for user domain."""


class InvalidRoleAssignment(UserDomainError):
    pass


class InactiveAccountError(UserDomainError):
    pass


class EmailNotConfirmedError(UserDomainError):
    pass


class TokenExpiredError(UserDomainError):
    pass


class TokenInvalidError(UserDomainError):
    pass