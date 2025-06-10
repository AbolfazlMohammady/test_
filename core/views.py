from django.conf import settings

from rest_framework import permissions ,status , viewsets 
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User
from .serializers import UserSeializer

import jwt


class LoginRegesterApiView(APIView):
    def post(self , request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        if not phone:
            return Response({'detail':"شمارت تلفن نمیتواند خالی باشد"},status=status.HTTP_400_BAD_REQUEST)
        
        if not password:
            return Response({'detail':"پسورد  نمیتواند خالی باشد"},status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(phone=phone).first()
        
        if user:
            if not user.check_password(password):
               return Response({'detail':"پسورد شما اشتباه است"},status=status.HTTP_400_BAD_REQUEST)
            user_exist = True

        else:
            data = {'phone':phone,
                    'password':password}
            
            serializer = UserSeializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                user.set_password(password)
                user.save()
                user_exist = False
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "کاربر با موفقیت ثبت نام کرد" if not user_exist else "ورود موفقیت‌آمیز"
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