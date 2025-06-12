from asyncio import timeout
from pickle import FALSE
from urllib.request import Request

from django.contrib.admin import action
from django.contrib.auth.hashers import check_password
from django.core.serializers import serialize
from django.db.models.sql import RawQuery
from django.template.context_processors import request
from django.core.cache import cache
from django.conf import settings
from pyexpat.errors import messages

from rest_framework import status, permissions
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import  TokenError

from .models import User
from .serializers import UserSerializer, RefreshTokenSerializer, \
    ProfileSerializer

import random
import jwt


class LoginRegisterView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        if not phone:
            return Response({"detail": "شماره تلفن نمیتواند خالی باشد"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({"detail": "پسورد نمیتواند خالی باشد"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone=phone).first()

        if user:
            if not user.check_password(password):
                return Response({"detail": "پسورد اشتباه است"},
                                status=status.HTTP_400_BAD_REQUEST)
            user_exist = True
        else:
            data = {
                "phone": phone,
                "password": password
            }
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                user.set_password(password)
                user.save()
                user_exist = False
            else:
                return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "ثبت نام با موفقیت انجام شد" if not user_exist\
                else "ورود موفقیت آمیز"
        }, status=status.HTTP_200_OK)


class RefreshTokenApi(APIView):
    def post(self, request, format=None):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {"error": "Refresh Token الزامی است"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            decoded_token = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )

            user_id = decoded_token.get('user_id')

            if not user_id:
                raise TokenError("Invalid token structure")

            user = User.objects.get(id=user_id)

            access_token = AccessToken.for_user(user)

            return Response(
                {'access': str(access_token)},
                status=status.HTTP_200_OK
            )

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )


class ProfileApiViewSet(ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request):
        try:
            queryset = User.objects.get(pk=request.user.id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = ProfileSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)



    def update(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, method=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response(
                {'detail': 'هردو فیلد رمز عبور قدیمی و رمز عبور جدید لازم هستند'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if check_password(old_password, request.user):
            return Response(
                {'detail': 'رمز عبور قدیمی اشتباه است.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response(
            {'detail': 'رمز عبور با موفقیت تغییر کرد'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, method=['post'], permission_classes=permissions.IsAuthenticated)
    def delete_account(self, request):
        user = request.user
        confirm = user.date.get('confirm')

        if not confirm != 'yes':
            return Response(
                {'detail': 'برای حذف این حساب باید تایید کنید'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_active=False
        user.save()
        return Response(
            {'detail': 'حساب کاربری با موفقیت حذف شد'},
            status=status.HTTP_200_OK
        )

# class PasswordResetRequestView(APIView):
#     def post(self, request):
#         seriaizer = PasswordResetRequestSerializer(data=request.data)
#         if not seriaizer.is_valid():
#             return Response(seriaizer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         phone = seriaizer.validated_data['phone']
#         try:
#             user = User.objects.get(phone=phone)
#         except User.DoesNotExist:
#             return Response(
#                 {'detail': 'کاربر با این شماره تلفن وجود ندارد'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         code = str(random.randint(1000, 9999))
#         cache.set(f"password_reset_{phone}", code, timeout=300)
#
#         print(f"کد بازیابی برای {phone}: {code}")
#         return Response(
#             {"detail": "کد بازیابی ارسال شد"},
#             status=status.HTTP_200_OK
#         )


# class PasswordConfirmRequestView(APIView):
#     def post(self, request):
#         serializer = PasswordResetConfirmSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         phone = serializer.validated_data['phone']
#         code = serializer.validated_data['code']
#         new_password = serializer.validated_data['new_password']
#
#         cached_code = cache.get(f"password_reset_{phone}")
#         if not cached_code or cached_code != code:
#             return Response(
#                 {"detail": "کد نامعتبر یا منقضی شده است"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         try:
#             user = User.objects.get(phone=phone)
#             user.set_password(new_password)
#             user.save()
#             cache.delete(f"password_reset_{phone}")
#             return Response(
#                 {"detail": "رمز عبور با موفقیت تغییر یافت"},
#                 status=status.HTTP_200_OK
#             )
#         except User.DoesNotExist:
#             return Response(
#                 {"detail": "کاربر یافت نشد"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
