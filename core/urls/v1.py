from django.urls import path
from core.views.v1.auth.login import LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login')
]
