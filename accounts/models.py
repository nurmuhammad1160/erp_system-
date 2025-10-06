# accounts/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from core.models import TimestampedModel, Branch
from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import GroupStatus


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email bo'lishi shart")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('type', User.UserType.SUPERUSER)
        return self.create_user(email, password, **extra_fields)


class User(TimestampedModel, AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        SUPERUSER = 'super_user', 'SuperUser'
        MANAGER = 'manager', 'Manager'
        ADMIN = 'admin', 'Admin'
        TEACHER = 'teacher', 'Teacher'
        SUPPORT_TEACHER = 'support_teacher', 'SupportTeacher'
        STUDENT = 'student', 'Student'

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    type = models.CharField(max_length=30, choices=UserType.choices, default=UserType.STUDENT)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # admin site kirishini belgilaydi
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.email



class ManagerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='manager_profile')
    position = models.CharField(max_length=120, blank=True)
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Manager: {self.user.get_full_name() or self.user.email}"


class AdminProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_profile')
    manager = models.ForeignKey(ManagerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='admins')
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Admin: {self.user.get_full_name() or self.user.email}"


class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile')
    speciality = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)  # 0.00 - 5.00


    def __str__(self):
        return f"Teacher: {self.user.get_full_name() or self.user.email}"


class SupportTeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_profile')
    related_teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='supporters')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Support: {self.user.get_full_name() or self.user.email}"


class StudentProfile(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('finished', 'Finished'),
        ('blocked', 'Blocked'),
    )
    group = models.ForeignKey('courses.Group', on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    parent_name = models.CharField(max_length=200, blank=True)
    parent_phone = models.CharField(max_length=30, blank=True)
    join_date = models.DateField(default=timezone.now)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active')


    def __str__(self):
        return f"Student: {self.user.get_full_name() or self.user.email}"

    def debit(self, amount):
        """Balance kamaytirish (to'lovlar yoki o'zgarishlar uchun)"""
        self.balance = max(0, self.balance - amount)
        self.save(update_fields=['balance'])

    def credit(self, amount):
        self.balance += amount
        self.save(update_fields=['balance'])


# Hozircha barcha userlar uchun profile yaratiladi
@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        t = instance.type
        if t == User.UserType.MANAGER:
            ManagerProfile.objects.get_or_create(user=instance)
        elif t == User.UserType.ADMIN:
            AdminProfile.objects.get_or_create(user=instance)
        elif t == User.UserType.TEACHER:
            TeacherProfile.objects.get_or_create(user=instance)
        elif t == User.UserType.SUPPORT_TEACHER:
            SupportTeacherProfile.objects.get_or_create(user=instance)
        else:
            StudentProfile.objects.get_or_create(user=instance)