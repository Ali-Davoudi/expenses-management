from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Expense(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=timezone.now)
    description = models.TextField()
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)

    def __str__(self):
        return str(self.user)

    class Meta:
        db_table = 'expense'
        ordering = ['-date']


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
