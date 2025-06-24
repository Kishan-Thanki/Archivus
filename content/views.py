# content/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny  # About Us content should be public

# Assuming your mixin is in 'core.mixins.response_mixins'
from core.mixins.response_mixins import APIResponseMixin

from .models import AboutUsContent, TeamMember
from .serializers import AboutUsContentSerializer

import logging
logger = logging.getLogger(__name__)

class AboutUsAPIView(APIView, APIResponseMixin):
    """
    API View for fetching About Us page content and team members.
    This is designed to serve a single, configurable 'About Us' page.
    """
    permission_classes = [AllowAny] # This endpoint is publicly accessible
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        try:
            # We use get_or_create with a fixed PK (e.g., 1) to ensure
            # there's always one AboutUsContent object. If it doesn't exist,
            # it creates one with default values from the model.
            about_content, created = AboutUsContent.objects.get_or_create(pk=1)

            # Serialize the AboutUsContent instance.
            # Pass the request context so serializers can build absolute URLs for images.
            serializer = AboutUsContentSerializer(about_content, context={'request': request})

            return self.success_response(
                data=serializer.data,
                message="About Us content fetched successfully." if not created else "About Us content created and fetched.",
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            # Log the full exception traceback for debugging
            logger.exception("Error fetching About Us content.")
            return self.error_response(
                message=f"An unexpected server error occurred while fetching About Us content. Please try again later. (Details: {str(e)})",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )