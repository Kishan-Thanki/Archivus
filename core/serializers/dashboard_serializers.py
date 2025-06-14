from rest_framework import serializers
from core.models import User, degree_level, program, course, Document, PointsHistory, academic_year, semester, upload_log
from django.db.models import Count, Sum


## --- Basic User Info Serializer ---
class BasicUserInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for basic user information, used in all dashboard responses.
    """
    degree_level = serializers.CharField(source='degree_level.name', read_only=True)
    program = serializers.CharField(source='program.name', read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "points",
            "degree_level",
            "program",
            "enrollment_year",
        ]
        read_only_fields = fields # Ensure these fields are read-only when used for output


## --- Student Dashboard Serializers ---

class StudentPointsHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for a single point history entry.
    """
    class Meta:
        model = PointsHistory
        fields = ["points", "reason", "timestamp"]


class StudentUploadedDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for documents uploaded by the student.
    """
    course_name = serializers.CharField(source='course.name', read_only=True)
    semester_name = serializers.CharField(source='semester.name', read_only=True)

    class Meta:
        model = Document
        fields = ["id", "title", "subject", "doc_type", "upload_timestamp", "status", "course_name", "semester_name"]


class StudentDashboardSerializer(serializers.Serializer):
    """
    Serializer for student-specific dashboard data.
    Note: This is a Serializer, not ModelSerializer, as it aggregates various data.
    """
    current_points = serializers.IntegerField()
    recent_points_history = StudentPointsHistorySerializer(many=True)
    uploaded_documents_summary = serializers.DictField() # { 'total': N, 'pending': M, 'approved': O }
    my_recent_uploads = StudentUploadedDocumentSerializer(many=True)
    my_program_info = serializers.DictField(allow_empty=True, required=False) # e.g., current program, degree level
    my_academic_progress = serializers.DictField(allow_empty=True, required=False) # e.g., enrolled courses, current semester


## --- Admin Dashboard Serializers ---

class AdminDashboardSerializer(serializers.Serializer):
    """
    Serializer for admin-specific dashboard data.
    Aggregates system-wide statistics.
    """
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    users_by_role = serializers.DictField() # { 'admin': N, 'student': M, 'staff': O }
    total_documents = serializers.IntegerField()
    documents_pending_review = serializers.IntegerField()
    documents_approved = serializers.IntegerField()
    recent_document_uploads = StudentUploadedDocumentSerializer(many=True) # Reusing for simplicity
    recent_upload_reviews = serializers.ListField(child=serializers.DictField(), required=False) # Detailed review logs


# You would define StaffDashboardSerializer similarly if you enable it
# class StaffDashboardSerializer(serializers.Serializer):
#    # ... specific fields for staff, e.g., documents requiring review, recent reviews performed