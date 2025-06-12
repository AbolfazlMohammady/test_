import re
from xml.etree.ElementInclude import default_loader

from django.core.files.storage import default_storage
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import BaseUserManager, AbstractUser

def validate_phone(value):
    if not value:
        raise ValidationError("شماره تلفن نمیتواند خالی باشد")
    if not re.match(r'^09\d{9}$', value):
        return ValidationError("شماره تلفن شما باید از 09 شروع شود و 11 رقم باشد0")

def path_image_user(instance, filename):
    model_name = instance.__class__.__name__.lower()
    return f"uploads/{model_name}/{instance.pk or 'new'}/{filename}"

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("شماره تلفن الزامی است")
        if not password:
            raise ValueError("پسورد الزامی است")

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        extra_fields.pop('password2', None)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            phone=phone,
            password=password,
            **extra_fields
        )

class User(AbstractUser):
    first_name = None
    last_name = None
    username = None
    fullname = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=6, choices=[('male', 'مرد'), ('female', 'زن')], blank=True, null=True)
    birth_date = models.DateField( blank=True, null=True)
    image = models.ImageField(upload_to=path_image_user, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(
        validators=[validate_phone],
        max_length = 11,
        unique = True
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.phone

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = self.__class__.objects.filter(pk=self.pk).first()
            if (
                old_instance
                and old_instance.image
                and old_instance.image.name
                and self.image != old_instance.image
            ):
                if default_storage.exists(old_instance.image.path):
                    default_storage.delete(old_instance.image.path)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image and default_storage.exists(self.image.path):
            default_storage.delete(self.image.path)
        super().delete(*args, **kwargs)