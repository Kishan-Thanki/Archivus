from .base import TimeStampedModel

from django.db import models

class DegreeLevel(TimeStampedModel):
    class Code(models.TextChoices):
        UG = 'UG', 'Undergraduate'
        PG = 'PG', 'Postgraduate'
        PHD = 'PHD', 'Doctorate'

    code = models.CharField(max_length=10, choices=Code.choices, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta(TimeStampedModel.Meta):
        pass

    def __str__(self):
        return self.name