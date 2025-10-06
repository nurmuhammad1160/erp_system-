# academics/models.py
from django.db import models
from django.utils import timezone
from core.models import TimestampedModel



class AttendanceStatus(models.TextChoices):
    PRESENT = 'present', 'Present'
    ABSENT = 'absent', 'Absent'
    LATE = 'late', 'Late'


class Attendance(TimestampedModel):
    group = models.ForeignKey('courses.Group', on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=AttendanceStatus.choices, default=AttendanceStatus.PRESENT)
    added_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('group', 'student', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.student.user.get_full_name()}: {self.status}"


class Homework(TimestampedModel):
    group = models.ForeignKey('courses.Group', on_delete=models.CASCADE, related_name='homeworks')
    teacher = models.ForeignKey('accounts.TeacherProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='homeworks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.group.name})"


def submission_upload_path(instance, filename):
    return f"submissions/homework_{instance.homework.id}/{instance.student.user.id}/{filename}"


class HomeworkSubmission(TimestampedModel):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to=submission_upload_path, null=True, blank=True)
    text = models.TextField(blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # 0-100
    checked_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='checked_submissions')
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('homework', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission by {self.student.user.get_full_name()} for {self.homework.title}"
