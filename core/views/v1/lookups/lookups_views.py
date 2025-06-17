from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics
from rest_framework.permissions import AllowAny

from core.models import DegreeLevel, Program
from core.serializers.lookups_serializers import DegreeLevelSerializer, ProgramSerializer


class DegreeLevelListView(generics.ListAPIView):
    """
    API endpoint that allows DegreeLevel data to be viewed.
    Provides a list of all available degree levels for dropdowns.
    """
    queryset = DegreeLevel.objects.all().order_by('name')
    serializer_class = DegreeLevelSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get a list of all available degree levels (e.g., Undergraduate, Postgraduate).",
        responses={
            200: openapi.Response('List of Degree Levels', DegreeLevelSerializer(many=True)),
            500: 'Server error fetching data.',
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ProgramListView(generics.ListAPIView):
    """
    API endpoint that allows Program data to be viewed.
    Provides a list of all available academic programs for dropdowns.
    """
    queryset = Program.objects.all().select_related('degree_level').order_by('name')
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get a list of all available academic programs. Includes associated degree level for display.",
        responses={
            200: openapi.Response('List of Programs', ProgramSerializer(many=True)),
            500: 'Server error fetching data.',
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)