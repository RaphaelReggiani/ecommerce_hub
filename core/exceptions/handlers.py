from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from ech.users.exceptions import UserDomainError


def custom_exception_handler(exc, context):
    """
    Custom global exception handler for domain-level errors.
    """

    response = exception_handler(exc, context)

    if response is not None:
        return response

    if isinstance(exc, UserDomainError):
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return None