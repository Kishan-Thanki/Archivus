from django.db import models
from .user import User
from .course import Course
from .semester import Semester

class Document(models.Model):
    INSEM = 'insem'
    ENDSEM = 'endsem'
    ASSIGNMENT = 'assignment'
    NOTES = 'notes'
    OTHER = 'other'

    DOC_TYPE_CHOICES = [
        (INSEM, 'Midterm Exam'),
        (ENDSEM, 'Final Exam'),
        (ASSIGNMENT, 'Assignment'),
        (NOTES, 'Study Notes'),
        (OTHER, 'Other'),
    ]

    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending Review'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')  # Using FileField instead of URL
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    doc_type = models.CharField(max_length=50, choices=DOC_TYPE_CHOICES)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, blank=True, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"{self.title} ({self.get_doc_type_display()})"

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"