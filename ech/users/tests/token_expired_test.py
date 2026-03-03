import pytest
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth import get_user_model
from ech.users.models import UserToken
from ech.users.services.registration_service import UserRegistrationService
from ech.users.exceptions import EmailTokenExpiredError

User = get_user_model()


@pytest.mark.django_db
class TestEmailTokenExpired:

    def test_expired_email_confirmation_token(self):

        user = User.objects.create_user(
            email="expired@test.com",
            password="StrongPassword123",
            user_name="Expired User",
        )

        user.is_active = False
        user.email_confirmed = False
        user.save(update_fields=["is_active", "email_confirmed"])

        token_obj = UserToken.objects.create(
            user=user,
            token="expiredtoken123",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            expires_at=timezone.now() - timedelta(hours=1),
        )

        with pytest.raises(EmailTokenExpiredError):
            UserRegistrationService.confirm_email("expiredtoken123")

        assert not UserToken.objects.filter(
            token="expiredtoken123"
        ).exists()

        user.refresh_from_db()
        assert user.is_active is False
        assert user.email_confirmed is False