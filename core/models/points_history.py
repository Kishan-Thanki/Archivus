from .base import TimeStampedModel
from .user import User
from django.db import models

class PointsHistory(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()

    class Meta(TimeStampedModel.Meta):
        ordering = ['-created_at']
        pass

    def __str__(self):
        return f"{self.user.email} - {self.points} pts"