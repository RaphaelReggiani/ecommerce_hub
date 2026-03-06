from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.password_validation import validate_password

from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

from ech.users.models import CustomUser

from rest_framework_simplejwt.tokens import RefreshToken

from ech.users.services.registration_service import UserRegistrationService
from ech.users.api.throttles import LoginRateThrottle

from .serializers import (
    UserRegisterInputSerializer,
    UserOutputSerializer,
    UserLoginInputSerializer,
    UserProfileSerializer,
    UserLogoutSerializer,
    PasswordResetRequestSerializer,
)

from ech.users.constants.messages import (
    MSG_SUCCESFULL_LOGOUT,
    MSG_RESPONSE_SUCCESFULL_RESET_LINK_SENT,
    MSG_RESPONSE_SUCCESFULL_PASSWORD_RESET,
    MSG_VALIDATION_ERROR_INVALID_RESET_LINK,
    MSG_VALIDATION_ERROR_UID,
    MSG_VALUE_ERROR_INVALID_OR_EXPIRED_TOKEN,
)


class UserRegisterApi(APIView):

    def post(self, request):

        serializer = UserRegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserRegistrationService.register_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            user_name=serializer.validated_data["user_name"],
        )

        output = UserOutputSerializer(user)

        return Response(
            output.data,
            status=status.HTTP_201_CREATED
        )


class ConfirmEmailApi(APIView):

    def post(self, request, token):

        user = UserRegistrationService.confirm_email(token)

        output = UserOutputSerializer(user)

        return Response(
            output.data,
            status=status.HTTP_200_OK
        )


class UserLoginApi(APIView):

    throttle_classes = [LoginRateThrottle]

    def post(self, request):

        serializer = UserLoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class UserLogoutApi(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = UserLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {"detail": MSG_SUCCESFULL_LOGOUT},
            status=status.HTTP_205_RESET_CONTENT
        )


class UserProfileApi(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserProfileSerializer(request.user)

        return Response(serializer.data)
    

class PasswordResetRequestApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = CustomUser.objects.get(user_email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

            send_mail(
                subject="Reset your E-commerce Hub password",
                message=f"Use the link to reset your password:\n{reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.user_email],
            )

        except CustomUser.DoesNotExist:
            pass

        return Response(
            {"detail": MSG_RESPONSE_SUCCESFULL_RESET_LINK_SENT},
            status=status.HTTP_200_OK,
        )
    

class PasswordResetConfirmApi(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not uid or not token or not new_password:
            raise ValidationError(MSG_VALIDATION_ERROR_UID)

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(pk=uid)
        except Exception:
            raise ValidationError(MSG_VALIDATION_ERROR_INVALID_RESET_LINK)

        if not default_token_generator.check_token(user, token):
            raise ValidationError(MSG_VALUE_ERROR_INVALID_OR_EXPIRED_TOKEN)

        try:
            validate_password(new_password, user)
        except DjangoValidationError as e:
            raise ValidationError({"password": e.messages})

        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": MSG_RESPONSE_SUCCESFULL_PASSWORD_RESET},
            status=status.HTTP_200_OK
        )