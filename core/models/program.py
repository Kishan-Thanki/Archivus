from django.db import models
from .degree_level import DegreeLevel

class Program(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True, null=True)
    degree_level = models.ForeignKey(DegreeLevel, on_delete=models.CASCADE)
    duration_years = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.degree_level.code})"

    class Meta:
        verbose_name = "Program"
        verbose_name_plural = "Programs"