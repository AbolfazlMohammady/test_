from rest_framework import serializers

from .models import User


class UserSeializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields= ['phone', "password"]
        extra_kwargs= {"password": {"write_only":True}}
