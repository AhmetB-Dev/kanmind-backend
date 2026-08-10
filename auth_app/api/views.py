"""API views for authentication and user lookup."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import User

from .serializers import (
    EmailCheckSerializer,
    LoginSerializer,
    RegistrationSerializer,
    UserSummarySerializer,
)


def _get_auth_data(user):
    """Return the token and public user data used by auth responses."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "fullname": user.fullname,
        "email": user.email,
        "user_id": user.id,
    }


class RegistrationView(APIView):
    """Register a user and return authentication data."""

    permission_classes = []

    def post(self, request):
        """Create a user from validated registration data."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(_get_auth_data(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticate a user and return a reusable API token."""

    permission_classes = []

    def post(self, request):
        """Validate credentials and return authentication data."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return Response(_get_auth_data(user))


class EmailCheckView(APIView):
    """Look up an existing user by email for board membership."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the public summary for the requested email address."""
        query = EmailCheckSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            email=query.validated_data["email"],
        )
        return Response(UserSummarySerializer(user).data)
