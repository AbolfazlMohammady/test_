from rest_framework import permissions ,status , viewsets , views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens im
from .models import User
from .serializers import UserSeializer


class LoginRegesterApiView(views.APIView):
    def post(self , request):
        phone = request.get('phone')
        password = request.get('password')

        if not phone:
            return Response({'detail':"شمارت تلفن نمیتواند خالی باشد"},status=status.HTTP_400_BAD_REQUEST)
        
        if not password:
            return Response({'detail':"پسورد  نمیتواند خالی باشد"},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({'detail':"user not found!!"},status=status.HTTP_400_BAD_REQUEST)
        
        if user:
            if not user.check_password(password):
               raise Response({'detail':"پسورد شما اشتباه است"},status=status.HTTP_400_BAD_REQUEST)
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
            

