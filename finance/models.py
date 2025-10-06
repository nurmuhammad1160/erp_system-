# finance/models.py
from django.db import models
from django.utils import timezone
from core.models import TimestampedModel


class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'Cash'
    CARD = 'card', 'Card'
    TRANSFER = 'transfer', 'Bank transfer'
    ONLINE = 'online', 'Online'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class Payment(TimestampedModel):
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=30, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_payments')
    approved_by = models.ForeignKey('accounts.AdminProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payments')
    note = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey('courses.Group', on_delete=models.SET_NULL, null=True, blank=True) 

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.amount} — {self.student.user.get_full_name()} ({self.payment_date.date()})"


class Expense(TimestampedModel):
    category = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    added_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.category}: {self.amount} ({self.date})"
