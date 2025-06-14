from .base import TimeStampedModel
from .program import Program

from django.db import models

class Course(TimeStampedModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)

    class Meta(TimeStampedModel.Meta):
        unique_together = ('program', 'code')

    def __str__(self):
        return f"{self.code} - {self.name}"