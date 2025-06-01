from django.urls import path

from .views import LoginRegesterApiView

urlpatterns = [
    path('login/',LoginRegesterApiView.as_view()),
]
