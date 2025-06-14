import logging

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.mixins.response_mixins import APIResponseMixin
from core.serializers.dashboard_serializers import (
    AdminDashboardSerializer,
    StudentDashboardSerializer,
    BasicUserInfoSerializer,
    # StaffDashboardSerializer, # Uncomment if you enable staff
)
from core.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

# --- Swagger Schema Definition (as you provided, just for context) ---
dashboard_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "user": openapi.Schema(type=openapi.TYPE_OBJECT, description="Basic user info"),
        "dashboard": openapi.Schema(type=openapi.TYPE_OBJECT, description="Dashboard data by role"),
    },
)

# --- DashboardView ---
class DashboardView(APIView, APIResponseMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get dashboard data based on user role.",
        responses={
            200: dashboard_response_schema,
            401: 'Unauthorized',
            403: 'Forbidden - Role not supported',
            500: 'Internal Server Error', # Added 500 to swagger docs
        },
        security=[{"Bearer": []}],
    )

    def get(self, request, *args, **kwargs):
        user = request.user
        role = getattr(user, "role", None)

        logger.info(f"User {user.email} (ID: {user.id}, Role: {role}) requested dashboard data.")

        try:
            if role == "admin":
                data = DashboardService.get_admin_dashboard_data(user)
                serializer = AdminDashboardSerializer(data=data) # Pass data to serializer
            # elif role == "staff":
            #     data = DashboardService.get_staff_dashboard_data(user)
            #     serializer = StaffDashboardSerializer(data=data) # Pass data to serializer
            elif role == "student":
                data = DashboardService.get_student_dashboard_data(user)
                serializer = StudentDashboardSerializer(data=data) # Pass data to serializer
            else:
                logger.warning(f"Dashboard request from user {user.email} with unsupported role: {role}")
                return self.error_response(
                    message="Dashboard not available for your role.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            # Validate the serializer data
            if not serializer.is_valid():
                logger.error(f"Dashboard data serialization failed for user {user.email} (Role: {role}): {serializer.errors}")
                # This should ideally not happen if DashboardService returns valid data,
                # but it's a good safeguard.
                return self.error_response(
                    message="Failed to serialize dashboard data.",
                    errors=serializer.errors,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            user_info = BasicUserInfoSerializer(user).data
            return self.success_response(
                data={"user": user_info, "dashboard": serializer.data},
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.exception(f"Unexpected error fetching dashboard for user {user.id}: {e}")
            return self.error_response(
                message="Unexpected server error fetching dashboard.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )