from django.db import models

class DegreeLevel(models.Model):
    UG = 'UG'
    PG = 'PG'
    PHD = 'PHD'

    CODE_CHOICES = [
        (UG, 'Undergraduate'),
        (PG, 'Postgraduate'),
        (PHD, 'Doctorate'),
    ]

    code = models.CharField(max_length=10, choices=CODE_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Degree Level"
        verbose_name_plural = "Degree Levels"