from django.db import models
from .program import Program

class Course(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        unique_together = ('program', 'code')