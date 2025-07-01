from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from core.models.degree_level import DegreeLevel
from core.models.program import Program
from core.models.course import Course
from core.models.document import Document
from core.models.semester import Semester
from core.models.academic_year import AcademicYear

from core.serializers.lookups_serializers import (
    DegreeLevelSerializer,
    ProgramSerializer,
    CourseSerializer,
    AcademicYearSerializer,
    SemesterSerializer,
)

from core.mixins.response_mixins import APIResponseMixin


class DegreeLevelListView(APIResponseMixin, generics.ListAPIView):
    queryset = DegreeLevel.objects.all().order_by('name')
    serializer_class = DegreeLevelSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get a list of all available degree levels (e.g., Undergraduate, Postgraduate).",
        responses={200: openapi.Response('List of Degree Levels', DegreeLevelSerializer(many=True))}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, message="Degree levels fetched successfully")


class ProgramListView(APIResponseMixin, generics.ListAPIView):
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Program.objects.select_related('degree_level').order_by('name')
        degree_level_id = self.request.query_params.get('degree_level_id')
        if degree_level_id:
            queryset = queryset.filter(degree_level_id=degree_level_id)
        return queryset

    @swagger_auto_schema(
        operation_description="Get a list of all academic programs. Optionally filter by degree_level_id.",
        manual_parameters=[
            openapi.Parameter('degree_level_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Optional: Filter programs by Degree Level ID', required=False)
        ],
        responses={200: openapi.Response('List of Programs', ProgramSerializer(many=True))}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, message="Programs fetched successfully")


class CourseListView(APIResponseMixin, generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Course.objects.select_related('program').order_by('name')
        program_id = self.request.query_params.get('program_id')
        if program_id:
            queryset = queryset.filter(program_id=program_id)
        return queryset

    @swagger_auto_schema(
        operation_description="Get a list of all available courses. Optional filtering by program_id.",
        manual_parameters=[
            openapi.Parameter('program_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Optional: Filter courses by Program ID', required=False)
        ],
        responses={200: openapi.Response('List of Courses', CourseSerializer(many=True))}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, message="Courses fetched successfully")


class AcademicYearListView(APIResponseMixin, generics.ListAPIView):
    queryset = AcademicYear.objects.all().order_by('-year_start')
    serializer_class = AcademicYearSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get a list of all available academic years (e.g., 2023-2024).",
        responses={200: openapi.Response('List of Academic Years', AcademicYearSerializer(many=True))}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, message="Academic years fetched successfully")


class SemesterListView(APIResponseMixin, generics.ListAPIView):
    serializer_class = SemesterSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Semester.objects.select_related('program', 'academic_year')
        program = self.request.query_params.get('program')
        academic_year = self.request.query_params.get('academic_year')
        if program:
            qs = qs.filter(program_id=program)
        if academic_year:
            qs = qs.filter(academic_year_id=academic_year)
        return qs.order_by('program__name', 'academic_year__year_start', 'number')

    @swagger_auto_schema(
        operation_description="Get a list of semesters, optionally filtered by program and academic_year.",
        manual_parameters=[
            openapi.Parameter('program', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Program ID", required=False),
            openapi.Parameter('academic_year', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Academic Year ID", required=False),
        ],
        responses={200: openapi.Response('List of Semesters', SemesterSerializer(many=True))}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, message="Semesters fetched successfully")


class DocumentTypeChoicesView(APIResponseMixin, APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get available document types for uploads.",
        responses={
            200: openapi.Response('Document Type Choices', openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'value': openapi.Schema(type=openapi.TYPE_STRING),
                        'label': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ))
        }
    )
    def get(self, request, *args, **kwargs):
        choices = [{'value': value, 'label': label} for value, label in Document.DocumentType.choices]
        return self.success_response(data=choices, message="Document types fetched successfully")


class SemesterNumberChoicesView(APIResponseMixin, APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get available semester numbers for document classification.",
        responses={
            200: openapi.Response('Semester Number Choices', openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'value': openapi.Schema(type=openapi.TYPE_STRING),
                        'label': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ))
        }
    )
    def get(self, request, *args, **kwargs):
        choices = [{'value': value, 'label': label} for value, label in Semester.SemesterNumber.choices]
        return self.success_response(data=choices, message="Semester numbers fetched successfully")
