from rest_framework import serializers
from django.contrib.auth import authenticate

from ech.users.constants.constants import (
    MAX_LENGTH_NAME,
    MIN_LENGTH_PASSWORD,
)

from ech.users.constants.messages import (
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
    email = serializers.EmailField()
    user_name = serializers.CharField()
    role = serializers.CharField()
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