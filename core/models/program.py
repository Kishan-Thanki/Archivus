from .base import TimeStampedModel
from .degree_level import DegreeLevel

from django.db import models

class Program(TimeStampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, blank=True, null=True)
    degree_level = models.ForeignKey(DegreeLevel, on_delete=models.CASCADE)
    duration_years = models.PositiveIntegerField(blank=True, null=True)

    class Meta(TimeStampedModel.Meta):
        pass

    def __str__(self):
        return f"{self.name} ({self.degree_level.code})"