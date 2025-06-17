from django.urls import path, re_path

from rest_framework import permissions

from drf_yasg import openapi
from drf_yasg.views import get_schema_view


from core.views.v1.auth.auth_views import (
    LoginView, LogoutView, RegisterView, RefreshTokenView,
)
from core.views.v1.dashboard.dashboard_views import DashboardView
from core.views.v1.lookups.lookups_views import DegreeLevelListView, ProgramListView

schema_view = get_schema_view(
    openapi.Info(
        title="Archivus ENDPOINTS",
        default_version='v1',
        description="API documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Authentication
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh'),

    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Lookups
    path('lookups/degree-levels/', DegreeLevelListView.as_view(), name='degree-level-list'),
    path('lookups/programs/', ProgramListView.as_view(), name='program-list'),

    # Swagger UI:
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

