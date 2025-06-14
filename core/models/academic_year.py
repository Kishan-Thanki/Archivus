import logging

from datetime import datetime

from .base import TimeStampedModel

from django.db import models
from django.db.models.signals import post_migrate

from django.dispatch import receiver

logger = logging.getLogger(__name__)

class AcademicYear(TimeStampedModel):
    year_start = models.PositiveIntegerField()
    year_end = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.year_start}-{self.year_end}"

    class Meta(TimeStampedModel.Meta):
        unique_together = ("year_start", "year_end")

@receiver(post_migrate)
def populate_academic_years(sender, **kwargs):
    if sender.label != 'core':
        return

    start_year = 2001
    current_year = datetime.now().year

    for year in range(start_year, current_year + 1):
        year_start = year
        year_end = year + 1

        if not AcademicYear.objects.filter(year_start=year_start, year_end=year_end).exists():
            AcademicYear.objects.create(year_start=year_start, year_end=year_end)
            logger.info(f"Created AcademicYear: {year_start}-{year_end}")