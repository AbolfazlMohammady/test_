from django.urls import path

from .views import LoginRegisterView, RefreshTokenApi, ProfileApiViewSet

profile_viewset = ProfileApiViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'update'
})

change_password_view = ProfileApiViewSet.as_view({
    'post': 'change_password'
})

delete_account_view = ProfileApiViewSet.as_view({
    'post': 'delete_account'
})

urlpatterns = [
    path('register/', LoginRegisterView.as_view(), name="register"),
    # path('login/', LoginApiView.as_view(), name="login"),
    path('refresh/', RefreshTokenApi.as_view(), name="refresh"),
    # path('password/reset/', PasswordResetRequestView.as_view(), name="password-reset"),
    # path('password/reset/confirm/', PasswordConfirmRequestView.as_view(), name="password-reset-confirm")
    # path('profile/', profile_viewset),
    path('profile/change_password/', ProfileApiViewSet.as_view({'post': 'change_password'})),
    path('profile/delete_account/', ProfileApiViewSet.as_view({'post': 'delete_account'})),
    path('profile/me/', ProfileApiViewSet.as_view({'get': 'retrieve'})),
]
