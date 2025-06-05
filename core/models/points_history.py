from django.db import models
from .user import User

class PointsHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    reason = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.points} points"

    class Meta:
        verbose_name = "Points History"
        verbose_name_plural = "Points Histories"
        ordering = ['-timestamp']