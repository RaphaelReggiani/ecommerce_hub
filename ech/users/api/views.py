from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ech.users.api.permissions import (
    IsAuthenticatedActiveAndEmailConfirmed,
    IsAuthenticatedAndActive,
)
from ech.users.api.throttles import LoginRateThrottle
from ech.users.constants.messages import (
    MSG_RESPONSE_SUCCESFULL_PASSWORD_RESET,
    MSG_RESPONSE_SUCCESFULL_RESET_LINK_SENT,
    MSG_SUCCESFULL_LOGOUT,
    MSG_VALIDATION_ERROR_UID,
    MSG_VALUE_ERROR_INVALID_OR_EXPIRED_TOKEN,
)
from ech.users.domain_events.dispatcher import DomainEventDispatcher
from ech.users.domain_events.events import (
    UserPasswordResetRequestedEvent,
    UserTokenInvalidEvent,
)
from ech.users.models import CustomUser
from ech.users.services.user_email_confirmation_service import (
    UserEmailConfirmationService,
)
from ech.users.services.user_log_service import UserLogService
from ech.users.services.user_password_reset_service import PasswordResetService
from ech.users.services.user_registration_service import UserRegistrationService
from ech.users.services.user_update_service import UserUpdateService
from ech.users.utils.request_metadata import (
    get_client_ip,
    get_request_id,
    get_user_agent,
)

from .serializers import (
    PasswordResetRequestSerializer,
    UserLoginInputSerializer,
    UserLogoutSerializer,
    UserOutputSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserRegisterInputSerializer,
)


class UserRegisterApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idempotency_key = request.headers.get("Idempotency-Key")

        user = UserRegistrationService.register_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            user_name=serializer.validated_data["user_name"],
            idempotency_key=idempotency_key,
        )

        UserLogService.log_user_registered(user=user)

        output = UserOutputSerializer(user)

        return Response(
            output.data,
            status=status.HTTP_201_CREATED,
        )


class ConfirmEmailApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token):
        try:
            user = UserEmailConfirmationService.confirm_email(token)
        except Exception:
            event = UserTokenInvalidEvent(
                token_type="email_confirmation",
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                request_id=get_request_id(request),
            )
            DomainEventDispatcher.dispatch(event)
            raise

        UserLogService.log_user_email_confirmed(user=user)

        output = UserOutputSerializer(user)

        return Response(
            output.data,
            status=status.HTTP_200_OK,
        )


class UserLoginApi(APIView):
    throttle_classes = [LoginRateThrottle]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginInputSerializer(data=request.data)

        if not serializer.is_valid():
            email = request.data.get("email")
            UserLogService.log_user_login_failed(email=email)
            raise ValidationError(serializer.errors)

        user = serializer.validated_data["user"]

        UserLogService.log_user_login_succeeded(user=user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class UserLogoutApi(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request):
        serializer = UserLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": MSG_SUCCESFULL_LOGOUT},
            status=status.HTTP_205_RESET_CONTENT,
        )


class UserProfileApi(APIView):
    permission_classes = [IsAuthenticatedActiveAndEmailConfirmed]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        changed_fields = list(serializer.validated_data.keys())

        updated_user = UserUpdateService.update_user(
            user=request.user,
            performed_by=request.user,
            **serializer.validated_data,
        )

        UserLogService.log_user_profile_updated(
            user=updated_user,
            changed_fields=changed_fields,
            performed_by=request.user,
        )

        output = UserProfileSerializer(updated_user)

        return Response(
            output.data,
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = CustomUser.objects.filter(user_email=email).first()
        if user:
            event = UserPasswordResetRequestedEvent(
                user_id=user.id,
                email=user.user_email,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                request_id=get_request_id(request),
            )
            DomainEventDispatcher.dispatch(event)

        PasswordResetService.request_password_reset(email=email)

        return Response(
            {"detail": MSG_RESPONSE_SUCCESFULL_RESET_LINK_SENT},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not token or not new_password:
            raise ValidationError(MSG_VALIDATION_ERROR_UID)

        try:
            user = PasswordResetService.reset_password(
                token=token,
                new_password=new_password,
            )
        except DjangoValidationError as exc:
            raise ValidationError({"password": exc.messages})
        except Exception:
            event = UserTokenInvalidEvent(
                token_type="password_reset",
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                request_id=get_request_id(request),
            )
            DomainEventDispatcher.dispatch(event)
            raise ValidationError(MSG_VALUE_ERROR_INVALID_OR_EXPIRED_TOKEN)

        UserLogService.log_user_password_changed(user=user)

        return Response(
            {"detail": MSG_RESPONSE_SUCCESFULL_PASSWORD_RESET},
            status=status.HTTP_200_OK,
        )
    
class CurrentUserApi(APIView):
    permission_classes = [IsAuthenticatedActiveAndEmailConfirmed]

    def get(self, request):
        output = UserOutputSerializer(request.user)

        return Response(
            output.data,
            status=status.HTTP_200_OK,
        )