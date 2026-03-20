from django.test import SimpleTestCase

from ech.users.constants.messages import (
    MSG_ERROR_USER_ALREADY_EXISTS,
    MSG_ERROR_RESTRICTED_ACCESS,
    MSG_ERROR_TOKEN_EXPIRED,
    MSG_ERROR_INVALID_TOKEN,
    MSG_AUTHENTICATION_FAILED_INACTIVE_ACCOUNT,
)

from ech.users.exceptions import (
    UserDomainError,
    UserAlreadyExistsError,
    InvalidRoleAssignmentError,
    InactiveAccountError,
    EmailNotConfirmedError,
    TokenError,
    TokenExpiredError,
    TokenInvalidError,
    EmailTokenInvalidError,
    EmailTokenExpiredError,
)


class UserDomainErrorTestCase(SimpleTestCase):
    def test_default_message_is_used_when_no_message_is_provided(self):
        """Ensure default message is used when no custom message is given."""
        error = UserDomainError()
        self.assertEqual(error.message, "User domain error.")
        self.assertEqual(str(error), "User domain error.")

    def test_custom_message_overrides_default(self):
        """Ensure custom message overrides the default message."""
        error = UserDomainError(message="Custom error message")
        self.assertEqual(error.message, "Custom error message")
        self.assertEqual(str(error), "Custom error message")


class UserAlreadyExistsErrorTestCase(SimpleTestCase):
    def test_uses_default_message(self):
        """Ensure default message is correctly assigned."""
        error = UserAlreadyExistsError()
        self.assertEqual(error.message, MSG_ERROR_USER_ALREADY_EXISTS)

    def test_inherits_from_user_domain_error(self):
        """Ensure inheritance from UserDomainError."""
        self.assertIsInstance(UserAlreadyExistsError(), UserDomainError)


class InvalidRoleAssignmentErrorTestCase(SimpleTestCase):
    def test_uses_default_message(self):
        """Ensure default message is correctly assigned."""
        error = InvalidRoleAssignmentError()
        self.assertEqual(error.message, MSG_ERROR_INVALID_TOKEN)

    def test_inherits_from_user_domain_error(self):
        """Ensure inheritance from UserDomainError."""
        self.assertIsInstance(InvalidRoleAssignmentError(), UserDomainError)


class InactiveAccountErrorTestCase(SimpleTestCase):
    def test_uses_default_message(self):
        """Ensure default message is correctly assigned."""
        error = InactiveAccountError()
        self.assertEqual(error.message, MSG_AUTHENTICATION_FAILED_INACTIVE_ACCOUNT)

    def test_inherits_from_user_domain_error(self):
        """Ensure inheritance from UserDomainError."""
        self.assertIsInstance(InactiveAccountError(), UserDomainError)


class EmailNotConfirmedErrorTestCase(SimpleTestCase):
    def test_uses_default_message(self):
        """Ensure default message is correctly assigned."""
        error = EmailNotConfirmedError()
        self.assertEqual(error.message, MSG_ERROR_RESTRICTED_ACCESS)

    def test_inherits_from_user_domain_error(self):
        """Ensure inheritance from UserDomainError."""
        self.assertIsInstance(EmailNotConfirmedError(), UserDomainError)


class TokenErrorTestCase(SimpleTestCase):
    def test_uses_default_message(self):
        """Ensure default message is correctly assigned."""
        error = TokenError()
        self.assertEqual(error.message, MSG_ERROR_INVALID_TOKEN)

    def test_inherits_from_user_domain_error(self):
        """Ensure TokenError inherits from UserDomainError."""
        self.assertIsInstance(TokenError(), UserDomainError)


class TokenExpiredErrorTestCase(SimpleTestCase):
    def test_uses_default_message(self):
        """Ensure expired token error uses correct message."""
        error = TokenExpiredError()
        self.assertEqual(error.message, MSG_ERROR_TOKEN_EXPIRED)

    def test_inherits_from_token_error(self):
        """Ensure TokenExpiredError inherits from TokenError."""
        self.assertIsInstance(TokenExpiredError(), TokenError)


class TokenInvalidErrorTestCase(SimpleTestCase):
    def test_uses_default_message(self):
        """Ensure invalid token error uses correct message."""
        error = TokenInvalidError()
        self.assertEqual(error.message, MSG_ERROR_INVALID_TOKEN)

    def test_inherits_from_token_error(self):
        """Ensure TokenInvalidError inherits from TokenError."""
        self.assertIsInstance(TokenInvalidError(), TokenError)


class EmailTokenInvalidErrorTestCase(SimpleTestCase):
    def test_uses_default_message(self):
        """Ensure email token invalid error uses correct message."""
        error = EmailTokenInvalidError()
        self.assertEqual(error.message, MSG_ERROR_INVALID_TOKEN)

    def test_inherits_from_token_error(self):
        """Ensure EmailTokenInvalidError inherits from TokenError."""
        self.assertIsInstance(EmailTokenInvalidError(), TokenError)


class EmailTokenExpiredErrorTestCase(SimpleTestCase):
    def test_uses_default_message(self):
        """Ensure email token expired error uses correct message."""
        error = EmailTokenExpiredError()
        self.assertEqual(error.message, MSG_ERROR_TOKEN_EXPIRED)

    def test_inherits_from_token_error(self):
        """Ensure EmailTokenExpiredError inherits from TokenError."""
        self.assertIsInstance(EmailTokenExpiredError(), TokenError)