from rest_framework import permissions ,status , viewsets , views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSeializer


class LoginRegesterApiView(views.APIView):
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
                        

