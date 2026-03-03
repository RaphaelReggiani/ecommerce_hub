import pytest
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth import get_user_model
from ech.users.models import UserToken
from ech.users.services.registration_service import UserRegistrationService
from ech.users.exceptions import EmailTokenInvalidError

User = get_user_model()


@pytest.mark.django_db
class TestEmailConfirmationFlow:

    def test_successful_email_confirmation(self):

        user = User.objects.create_user(
            email="confirm@test.com",
            password="StrongPassword123",
            user_name="Confirm User",
        )

        user.is_active = False
        user.email_confirmed = False
        user.save(update_fields=["is_active", "email_confirmed"])

        token_obj = UserToken.create_token(
            user=user,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            hours_valid=24,
        )

        returned_user = UserRegistrationService.confirm_email(token_obj.token)

        user.refresh_from_db()

        assert user.is_active is True
        assert user.email_confirmed is True

        assert returned_user.id == user.id

        assert not UserToken.objects.filter(
            token=token_obj.token
        ).exists()

    def test_token_cannot_be_reused(self):

        user = User.objects.create_user(
            email="reuse@test.com",
            password="StrongPassword123",
            user_name="Reuse User",
        )

        user.is_active = False
        user.email_confirmed = False
        user.save(update_fields=["is_active", "email_confirmed"])

        token_obj = UserToken.create_token(
            user=user,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            hours_valid=24,
        )

        UserRegistrationService.confirm_email(token_obj.token)

        with pytest.raises(EmailTokenInvalidError):
            UserRegistrationService.confirm_email(token_obj.token)