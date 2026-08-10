"""Serializers for registration, login, and user lookup."""

from django.contrib.auth import authenticate
from rest_framework import serializers

from auth_app.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration data and create a new user."""

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        """Ensure both submitted passwords match."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        """Create the user without persisting the repeated password."""
        validated_data.pop("repeated_password")
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Validate email and password credentials."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the credentials and expose the authenticated user."""
        user = authenticate(
            email=attrs["email"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")

        attrs["user"] = user
        return attrs


class EmailCheckSerializer(serializers.Serializer):
    """Validate the email query parameter used for member lookup."""

    email = serializers.EmailField()


class UserSummarySerializer(serializers.ModelSerializer):
    """Expose the public user fields embedded in API responses."""

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]
