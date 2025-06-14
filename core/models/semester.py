import logging

from .base import TimeStampedModel
from .program import Program
from .academic_year import AcademicYear

from django.db import models
from django.db.models import TextChoices

logger = logging.getLogger(__name__)

class Semester(TimeStampedModel):
    class SemesterName(TextChoices):
        SUMMER = 'Summer', 'Summer'
        WINTER = 'Winter', 'Winter'

    class SemesterNumber(TextChoices):
        ONE = '1', '1'
        TWO = '2', '2'
        THREE = '3', '3'
        FOUR = '4', '4'
        FIVE = '5', '5'
        SIX = '6', '6'
        SEVEN = '7', '7'
        EIGHT = '8', '8'

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="semesters", null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, choices=SemesterName.choices)

    number = models.CharField(max_length=100, choices=SemesterNumber.choices, null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        unique_together = ("program", "academic_year", "name", "number")
        ordering = ['program', 'academic_year__year_start', 'number']

    def __str__(self):
        program_display = self.program.code if self.program else "N/A"
        number_display = f" {self.number}" if self.number else ""
        return f"{program_display} - {self.name}{number_display} {self.academic_year}"