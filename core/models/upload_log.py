from .base import TimeStampedModel, DocumentStatus
from .user import User
from .document import Document

from django.db import models

class UploadLog(TimeStampedModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    review_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=DocumentStatus.choices)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta(TimeStampedModel.Meta):
        pass

    def __str__(self):
        return f"{self.document.title} - {self.status}"