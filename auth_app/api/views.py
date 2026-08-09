from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from auth_app.models import User
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    EmailCheckSerializer,
    LoginSerializer,
    RegistrationSerializer,
    UserSummarySerializer,
)


class RegistrationView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            self._get_auth_data(user),
            status=status.HTTP_201_CREATED,
        )

    def _get_auth_data(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        return {
            "token": token.key,
            "fullname": user.fullname,
            "email": user.email,
            "user_id": user.id,
        }


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id,
            }
        )


class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = EmailCheckSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        user = get_object_or_404(
            User,
            email=query.validated_data["email"],
        )
        return Response(UserSummarySerializer(user).data)
