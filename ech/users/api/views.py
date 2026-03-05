from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from ech.users.services.registration_service import UserRegistrationService
from ech.users.api.throttles import LoginRateThrottle

from .serializers import (
    UserRegisterInputSerializer,
    UserOutputSerializer,
    UserLoginInputSerializer,
    UserProfileSerializer,
    UserLogoutSerializer,
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
            {"detail": "Logout successful"},
            status=status.HTTP_205_RESET_CONTENT
        )


class UserProfileApi(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserProfileSerializer(request.user)

        return Response(serializer.data)