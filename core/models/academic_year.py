from django.db import models

class AcademicYear(models.Model):
    year_start = models.PositiveIntegerField()
    year_end = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.year_start}-{self.year_end}"

    class Meta:
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"
        unique_together = ('year_start', 'year_end')