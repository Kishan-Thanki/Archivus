from .base import TimeStampedModel, DocumentStatus, SemesterNumber
from .academic_year import AcademicYear
from .user import User
from .course import Course

from django.db import models
from django.db.models import TextChoices

class Document(TimeStampedModel):
    class DocumentType(TextChoices):
        INSEM = 'insem', 'Midterm Exam'
        ENDSEM = 'endsem', 'Final Exam'
        ASSIGNMENT = 'assignment', 'Assignment'
        NOTES = 'notes', 'Study Notes'
        OTHER = 'other', 'Other'

    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    title = models.CharField(max_length=200)
    doc_type = models.CharField(max_length=50, choices=DocumentType.choices)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, blank=True, null=True)

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE,
                                      related_name='documents', null=True, blank=True)
    semester_number = models.CharField(max_length=2, choices=SemesterNumber.choices,
                                       null=True, blank=True,
                                       help_text="e.g., 1, 2, 3 (Optional)")

    status = models.CharField(max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.PENDING)

    def __str__(self):
        year_info = f" {self.academic_year}" if self.academic_year else ""
        sem_info = f" Semester {self.get_semester_number_display()}" if self.semester_number else ""
        return f"{self.title} ({self.get_doc_type_display()}){year_info}{sem_info}"

    class Meta(TimeStampedModel.Meta):
        permissions = [
            ("can_review_document", "Can review submitted documents"),
            ("can_publish_document", "Can publish approved documents"),
            ("can_access_confidential", "Can access confidential documents"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view',)