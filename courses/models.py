# courses/models.py
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from core.models import TimestampedModel


class CourseLevel(models.TextChoices):
    BEGINNER = 'beginner', 'Beginner'
    INTERMEDIATE = 'intermediate', 'Intermediate'
    ADVANCED = 'advanced', 'Advanced'


class Course(TimestampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_weeks = models.PositiveIntegerField(default=4)
    level = models.CharField(max_length=30, choices=CourseLevel.choices, default=CourseLevel.BEGINNER)
    created_by = models.ForeignKey('accounts.AdminProfile', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['slug']), models.Index(fields=['title'])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class GroupStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    FINISHED = 'finished', 'Finished'
    ARCHIVED = 'archived', 'Archived'


class Group(TimestampedModel):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='groups')
    teacher = models.ForeignKey('accounts.TeacherProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='groups')
    support_teacher = models.ForeignKey('accounts.SupportTeacherProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='support_groups')
    students = models.ManyToManyField('accounts.StudentProfile', blank=True, related_name='groups')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=GroupStatus.choices, default=GroupStatus.ACTIVE)

    class Meta:
        unique_together = ('name', 'course')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} — {self.course.title}"

    def active_students_count(self):
        return self.students.filter(status='active').count()


def material_upload_path(instance, filename):
    return f"materials/course_{instance.course.id if instance.course else 'na'}/{timezone.now().strftime('%Y/%m/%d')}/{filename}"


class Material(TimestampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=material_upload_path, blank=True, null=True)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='materials')

    def __str__(self):
        return self.title
