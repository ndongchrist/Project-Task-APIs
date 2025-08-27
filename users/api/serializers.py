# serializers.py

from typing import Dict, Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'phone',
            'email',
        ]
        read_only_fields = fields


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(label=_("Email"), write_only=True)
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'}, trim_whitespace=False, write_only=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(_('Unable to log in with provided credentials.'), code='authorization')

        if not user.check_password(password):
            raise serializers.ValidationError(_('Unable to log in with provided credentials.'), code='authorization')

        data = super().validate(attrs)
        data['user'] = UserSerializer(user, context=self.context).data
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        data = super().validate(attrs)
        token = self.context['view'].get_token()
        user = token.user
        data['user'] = UserSerializer(user, context=self.context).data
        return data



class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=255, required=False, allow_blank=True)
    

    class Meta:
        model = User
        fields = [
            "email", "password", "password_confirm", "first_name", "last_name", "phone"
        ]

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("email_in_use"))
        return value

    def validate_password(self, value: str) -> str:
        try:
            validate_password(value)
        except ValidationError:
            raise serializers.ValidationError(_("invalid_password"))
        return value

    def validate_has_accepted_terms(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError(_("must_accept_terms"))
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data.get("password") != data.get("password_confirm"):
            raise serializers.ValidationError(_("password_mismatch"))
        return data

    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop("password_confirm")
        validated_data["is_active"] = True
        user = User.objects.create_user(**validated_data)
        user.save()
        return user

    def to_representation(self, instance: User) -> Dict[str, Any]:
        return {
            "id": str(instance.pk),
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "phone": instance.phone,}


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value: str) -> str:
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("user_not_found"))
        return value