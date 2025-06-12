from enum import unique

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    def validate_refresh(self, value):
        if not value:
            raise serializers.ValidationError("رفرش توکن نمیتواند خالی باشد")

        return value


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["fullname", "gender", "birth_date", "image", "email", "phone"]
        read_only_fields = ['phone']


# class PasswordResetRequestSerializer(serializers.Serializer):
#     phone = serializers.CharField(required=True)
#
#
# class PasswordResetConfirmSerializer(serializers.Serializer):
#     phone = serializers.CharField(required=True)
#     code = serializers.CharField(required=True, max_length=10)
#     new_password = serializers.CharField(required=True)
