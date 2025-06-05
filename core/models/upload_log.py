from django.db import models
from .document import Document
from .user import User

class UploadLog(models.Model):
    APPROVED = 'approved'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    review_timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.document.title} - {self.status}"

    class Meta:
        verbose_name = "Upload Log"
        verbose_name_plural = "Upload Logs"
        ordering = ['-review_timestamp']