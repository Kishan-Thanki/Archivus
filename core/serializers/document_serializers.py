# core/serializers/document_serializers.py

from rest_framework import serializers
from core.models import Document, Course, AcademicYear, User
from core.models.base import SemesterNumber, DocumentStatus
from core.services.document_service import DocumentService


# --- Existing Lookups Serializers (Modified with ref_name) ---
class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'
        ref_name = 'DocumentAcademicYearSerializer' # <--- ADD THIS LINE with a UNIQUE NAME

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        ref_name = 'DocumentCourseSerializer' # <--- ADD THIS LINE with a UNIQUE NAME (good practice)

# --- Document Upload Serializer ---
class DocumentUploadSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    academic_year = serializers.PrimaryKeyRelatedField(queryset=AcademicYear.objects.all())
    semester_number = serializers.ChoiceField(choices=SemesterNumber.choices)
    doc_type = serializers.ChoiceField(choices=Document.DocumentType.choices)

    class Meta:
        model = Document
        fields = [
            'file', 'title', 'doc_type', 'course',
            'academic_year', 'semester_number'
        ]
        read_only_fields = ['uploader', 'status', 'file_format']

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to upload documents.")

        try:
            return DocumentService.create_document(validated_data, request.user)
        except serializers.ValidationError as e:
            raise e
        except Exception as e:
            raise serializers.ValidationError(f"Document upload failed: {e}")


# --- Document Update Serializer ---
class DocumentUpdateSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    academic_year = serializers.PrimaryKeyRelatedField(queryset=AcademicYear.objects.all(), required=False, allow_null=True)
    semester_number = serializers.ChoiceField(choices=SemesterNumber.choices, required=False)
    doc_type = serializers.ChoiceField(choices=Document.DocumentType.choices, required=False)

    class Meta:
        model = Document
        fields = [
            'title', 'doc_type', 'course',
            'academic_year', 'semester_number'
        ]
        extra_kwargs = {
            'title': {'required': False},
        }

    def update(self, instance, validated_data):
        document_id = instance.id
        try:
            return DocumentService.update_document_metadata(document_id, validated_data)
        except serializers.ValidationError as e:
            raise e
        except Exception as e:
            raise serializers.ValidationError(f"Document update failed: {e}")

# --- Document Retrieve/List Serializer ---
class DocumentRetrieveSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    academic_year = AcademicYearSerializer()
    uploader = serializers.ReadOnlyField(source='uploader.email')
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'doc_type', 'course', 'academic_year',
            'semester_number', 'file_url', 'uploader', 'status',
            'created_at', 'updated_at', 'file_format',
        ]
        read_only_fields = [
            'id', 'file_url', 'uploader', 'status', 'created_at',
            'updated_at', 'file_format'
        ]

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None

# --- Document Status Change Serializer ---
class DocumentStatusChangeSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=DocumentStatus.choices, required=True)