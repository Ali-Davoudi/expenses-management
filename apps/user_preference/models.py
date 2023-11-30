from django.db import models
from django.contrib.auth.models import User


class UserPreference(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(f"{self.user}'s preferences")

    class Meta:
        db_table = 'user_preference'
