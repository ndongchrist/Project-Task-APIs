# api.py

import logging
from typing import Dict, Any

from django.conf import settings
from django.contrib.auth import get_user_model, logout
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse, OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.api.serializers import RegisterSerializer, EmailSerializer, CustomTokenObtainPairSerializer, UserSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Tokens generated successfully.",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "user": {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "email": "john.doe@example.com",
                                "first_name": "John",
                                "last_name": "Doe",
                                "fullname": "John Doe"
                            }
                        }
                    )
                ]
            ),
            401: OpenApiResponse(description="Invalid credentials."),
        },
        description="Obtain JWT access and refresh tokens for authentication."
    )
    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        req_data: Dict[str, Any] = request.data.copy()
        email: str = req_data.get("email")

        if not email:
            raise AuthenticationFailed(_("Email is required for login"))

        try:
            current_user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": _("User not found")}, status=status.HTTP_404_NOT_FOUND)

        if not current_user.is_active:
            return Response(
                {
                    "message": _("Account not activated. Check your email to confirm your account."),
                    "error_code": "account_not_activated",
                },
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        serializer = self.get_serializer(data=request.data, context={"request": request})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.info("Error: %s", e)
            return Response(
                {
                    "message": _("Credentials are invalid or do not match."),
                    "error_code": "invalid_credentials",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Token refreshed successfully.",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "user": {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "email": "john.doe@example.com",
                                "first_name": "John",
                                "last_name": "Doe",
                                "fullname": "John Doe"
                            }
                        }
                    )
                ]
            ),
            401: OpenApiResponse(description="Invalid or expired refresh token."),
        },
        description="Refreshes the JWT access token using a valid refresh token."
    )
    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        try:
            response = super().post(request, *args, **kwargs)
            # Add user data to the response
            token = self.get_token()
            user = token.user
            response.data['user'] = UserSerializer(user, context={'request': request}).data
            return response
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return Response(
                {"error": _("Token refresh failed."), "error_code": "token_refresh_failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        try:
            Token.objects.filter(user=request.user).delete()
            logout(request)
            return Response({"message": _("Successfully logged out.")}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during logout for user {request.user.email}: {str(e)}")
            return Response(
                {"message": _("An error occurred during logout."), "error_code": "logout_failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Registration failed for request {request.data}: {str(e)}")
                return Response(
                    {"error": _("Registration failed.")},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)