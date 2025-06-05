from django.db import models
from .academic_year import AcademicYear

class Semester(models.Model):
    FALL = 'Fall'
    SPRING = 'Spring'
    SUMMER = 'Summer'
    WINTER = 'Winter'

    NAME_CHOICES = [
        (FALL, 'Fall'),
        (SPRING, 'Spring'),
        (SUMMER, 'Summer'),
        (WINTER, 'Winter'),
    ]

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=NAME_CHOICES)
    number = models.PositiveIntegerField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.academic_year}"

    class Meta:
        verbose_name = "Semester"
        verbose_name_plural = "Semesters"
        unique_together = ('academic_year', 'name')