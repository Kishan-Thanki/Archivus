from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from core.models.degree_level import DegreeLevel
from core.models.program import Program
from core.models.course import Course
from core.models.document import Document
from core.models.semester import Semester
from core.models.academic_year import AcademicYear

from core.serializers.lookups_serializers import DegreeLevelSerializer, ProgramSerializer, CourseSerializer, AcademicYearSerializer

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

class CourseListView(generics.ListAPIView):
    """
    API endpoint that allows Course data to be viewed.
    Provides a list of all available courses for dropdowns in document upload form.
    """
    queryset = Course.objects.all().select_related('program').order_by('name')
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get a list of all available courses. Includes program ID for potential filtering.",
        responses={
            200: openapi.Response('List of Courses', CourseSerializer(many=True)),
            500: 'Server error fetching data.',
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class AcademicYearListView(generics.ListAPIView):
    """
    API endpoint that allows AcademicYear data to be viewed.
    Provides a list of all available academic years for dropdowns in document upload form.
    """
    queryset = AcademicYear.objects.all().order_by('-year_start') # Order by newest year first
    serializer_class = AcademicYearSerializer
    permission_classes = [AllowAny] # Following your existing permission setup

    @swagger_auto_schema(
        operation_description="Get a list of all available academic years (e.g., 2023-2024).",
        responses={
            200: openapi.Response('List of Academic Years', AcademicYearSerializer(many=True)),
            500: 'Server error fetching data.',
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DocumentTypeChoicesView(APIView):
    """
    API endpoint that provides the choices for document types (e.g., Insem, Endsem).
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get available document types for uploads.",
        responses={
            200: openapi.Response('Document Type Choices', openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'value': openapi.Schema(type=openapi.TYPE_STRING, description='Internal choice value'),
                        'label': openapi.Schema(type=openapi.TYPE_STRING, description='Display label for the choice')
                    }
                )
            )),
            500: 'Server error fetching data.',
        },
    )
    def get(self, request, *args, **kwargs):
        choices = []
        for value, label in Document.DocumentType.choices:
            choices.append({'value': value, 'label': label})
        return Response(choices, status=status.HTTP_200_OK)


class SemesterNumberChoicesView(APIView):
    """
    API endpoint that provides the choices for semester numbers (e.g., 1, 2, 3).
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get available semester numbers for document classification.",
        responses={
            200: openapi.Response('Semester Number Choices', openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'value': openapi.Schema(type=openapi.TYPE_STRING, description='Internal choice value'),
                        'label': openapi.Schema(type=openapi.TYPE_STRING, description='Display label for the choice')
                    }
                )
            )),
            500: 'Server error fetching data.',
        },
    )
    def get(self, request, *args, **kwargs):
        choices = []
        for value, label in Semester.SemesterNumber.choices:
            choices.append({'value': value, 'label': label})
        return Response(choices, status=status.HTTP_200_OK)