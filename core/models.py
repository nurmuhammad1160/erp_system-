# core/models.py
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """Abstract model: created_at, updated_at"""
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Branch(TimestampedModel):
    """Agar bir nechta filial bo'lsa - manzili va manageri"""
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"
