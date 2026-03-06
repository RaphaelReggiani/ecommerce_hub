from rest_framework import serializers
from django.contrib.auth import authenticate
from ech.users.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

from ech.users.constants.constants import (
    MAX_LENGTH_NAME,
    MIN_LENGTH_PASSWORD,
)

from ech.users.constants.messages import (
    MSG_VALUE_ERROR_INVALID_OR_EXPIRED_TOKEN,
    MSG_AUTHENTICATION_FAILED_CREDENTIALS,
    MSG_AUTHENTICATION_FAILED_INACTIVE_ACCOUNT,
    MSG_AUTHENTICATION_EMAIL_NOT_CONFIRMED,
)


class UserRegisterInputSerializer(serializers.Serializer):
    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True,
        min_length=MIN_LENGTH_PASSWORD,
    )

    user_name = serializers.CharField(max_length=MAX_LENGTH_NAME)


class UserOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField(source="user_email")
    user_name = serializers.CharField()
    role = serializers.CharField(source="user_role")
    is_active = serializers.BooleanField()
    email_confirmed = serializers.BooleanField()

class UserLoginInputSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            user_email=attrs["email"],
            password=attrs["password"],
        )

        if not user:
            raise serializers.ValidationError(MSG_AUTHENTICATION_FAILED_CREDENTIALS)

        if not user.is_active:
            raise serializers.ValidationError(MSG_AUTHENTICATION_FAILED_INACTIVE_ACCOUNT)
            
        if not user.email_confirmed:
            raise serializers.ValidationError(MSG_AUTHENTICATION_EMAIL_NOT_CONFIRMED)

        attrs["user"] = user
        return attrs
    

class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except Exception:
            raise serializers.ValidationError(MSG_VALUE_ERROR_INVALID_OR_EXPIRED_TOKEN)
    

class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ["user_email", "user_name"]


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()