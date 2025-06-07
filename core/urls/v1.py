from django.contrib.auth.views import LogoutView
from django.urls import path

from core.views.v1.auth.auth_views import (
    LoginView,
    LogoutView,
    RegisterView,
    RefreshTokenView,
)

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh'),
]

