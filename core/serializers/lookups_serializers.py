from rest_framework import serializers
from core.models import DegreeLevel, Program, Course, AcademicYear

class DegreeLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DegreeLevel
        fields = ['code', 'name']

class ProgramSerializer(serializers.ModelSerializer):
    degree_level_name = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = ['id', 'name', 'degree_level_id', 'degree_level_name']

    def get_degree_level_name(self, obj):
        return obj.degree_level.name if obj.degree_level else None

class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for the Course model, providing essential fields for lookup.
    """
    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'program']

class AcademicYearSerializer(serializers.ModelSerializer):
    """
    Serializer for the AcademicYear model, providing essential fields for lookup.
    """
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = AcademicYear
        fields = ['id', 'year_start', 'year_end', 'display_name']

    def get_display_name(self, obj):
        return f"{obj.year_start}-{obj.year_end}"