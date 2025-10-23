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
    status = models.CharField(max_length=30, choices=[('submitted', 'Submitted'), ('graded', 'Graded'), ('late', 'Late')], default='submitted')

    class Meta:
        unique_together = ('homework', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission by {self.student.user.get_full_name()} for {self.homework.title}"


class Grades(models.Model):
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE, related_name='grades')
    homework = models.ForeignKey(HomeworkSubmission, on_delete=models.CASCADE, related_name='grades')
    average_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # 0-100
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='grades', null=True, blank=True)
    
    
    class Meta:
        unique_together = ('student', 'homework')
        ordering = ['-average_score']

    def __str__(self):
        # self.homework is a HomeworkSubmission instance; its .homework attribute is the Homework
        hw_title = getattr(self.homework, 'homework', None)
        hw_title = hw_title.title if hw_title and getattr(hw_title, 'title', None) else str(self.homework)
        return f"{self.student.user.get_full_name()} - {hw_title}: {self.average_score}"

    @property
    def submission(self):
        """Backwards-friendly alias: return the HomeworkSubmission instance."""
        return self.homework

    @property
    def homework_obj(self):
        """Return the Homework (assignment) instance for this grade, if available."""
        return getattr(self.homework, 'homework', None)

    @property
    def course_obj(self):
        """Return a Course instance associated with this grade if set, otherwise try to infer from the submission's group."""
        if self.course:
            return self.course
        hw = self.homework
        if hw and getattr(hw, 'homework', None) and getattr(hw.homework, 'group', None):
            return getattr(hw.homework.group, 'course', None)
        return None

    def letter_grade(self):
        """Return a simple letter grade based on average_score (A-F)."""
        if self.average_score is None:
            return None
        s = float(self.average_score)
        if s >= 90:
            return 'A'
        if s >= 80:
            return 'B'
        if s >= 70:
            return 'C'
        if s >= 60:
            return 'D'
        return 'F'


class LessonSchedule(TimestampedModel):
    group = models.ForeignKey('courses.Group', on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.PositiveSmallIntegerField(choices=[(1, 'Dushanba-Chorshanba-Juma'), (2, 'Seshanba-Payshanba-Shanba'), (3, 'Dushanba-Juma'), (4, 'Dushanba-Shanba')])
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True, null=True) 

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.start_time} - {self.end_time}"