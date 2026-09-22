from typing import Any

from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as TOPSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer as TRSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
        )


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "telegram_username")


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for User instance creation
    """

    class Meta:
        model = User
        fields = ("username", "email", "password")


class TokenObtainPairSerializer(TOPSerializer):
    """
    Serializer for Token obtainment
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        data = super().validate(attrs)

        if self.user:
            data["username"] = self.user.username
            data["email"] = self.user.email
            update_last_login(User, self.user)

        return data


class TokenRefreshSerializer(TRSerializer):
    """
    Serializer for token refreshment
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        data = super().validate(attrs)

        refresh_token_str = attrs["refresh"]
        refresh_token = RefreshToken(refresh_token_str)

        user_id = refresh_token.payload.get("user_id")
        if user_id:
            user = User.objects.get(id=user_id)
            data["username"] = user.username
            data["email"] = user.email

        return data
