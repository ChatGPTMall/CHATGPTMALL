from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from rest_framework import serializers

from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, max_length=32, write_only=True, validators=[validate_password])
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    home_name = serializers.CharField(required=True)
    home_key = serializers.CharField(required=True)

    class Meta:
        model = User
        exclude = (
            'id',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
            'reset_token',
            'premium',
            "access",
            "purchased_on",
        )
        read_only_fields = (
            'user_id',
            'is_superuser',
            'is_staff',
            'is_active',
            'joined_on',
        )


class UserSerializer(serializers.ModelSerializer):
    home_name = serializers.SerializerMethodField(read_only=True)
    home_key = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        exclude = (
            'id',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
            'reset_token',
            'premium',
            "access",
            "purchased_on",
            "room",
            "password"
        )
        read_only_fields = (
            "home_name",
            "home_key",
        )

    def get_home_name(self, user):
        return user.room.room_id if user.room else None

    def get_home_key(self, user):
        return user.room.room_key if user.room else None
