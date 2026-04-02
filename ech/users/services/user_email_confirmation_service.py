from django.db import transaction

from ech.users.exceptions import (
    EmailTokenExpiredError,
    EmailTokenInvalidError,
)
from ech.users.selectors import get_email_confirmation_token


class UserEmailConfirmationService:
    """
    Handles user email confirmation flow.
    """

    @staticmethod
    @transaction.atomic
    def confirm_email(token: str):
        token_obj = get_email_confirmation_token(token)

        if not token_obj:
            raise EmailTokenInvalidError()

        if token_obj.is_expired():
            token_obj.delete()
            raise EmailTokenExpiredError()

        user = token_obj.user
        user.is_active = True
        user.email_confirmed = True
        user.save(update_fields=["is_active", "email_confirmed"])

        token_obj.delete()

        return user