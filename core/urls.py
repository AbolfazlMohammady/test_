from django.urls import path

from .views import LoginRegesterApiView, RefreshTokenApi

urlpatterns = [
    path('login/',LoginRegesterApiView.as_view()),
    path('refresh/', RefreshTokenApi.as_view()),
]
