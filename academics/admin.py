from django.contrib import admin
from .models import Attendance, Homework, HomeworkSubmission, LessonSchedule


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'student_name', 'group_name', 'status', 'added_by')
    list_filter = ('status', 'group', 'date')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'group__name')
    ordering = ('-date',)

    def student_name(self, obj):
        return obj.student.user.get_full_name()
    student_name.short_description = 'Student'

    def group_name(self, obj):
        return obj.group.name
    group_name.short_description = 'Group'


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'group_name', 'teacher_name', 'deadline')
    search_fields = ('title', 'group__name', 'teacher__user__first_name', 'teacher__user__last_name')
    list_filter = ('group', 'deadline')
    ordering = ('-deadline',)

    def group_name(self, obj):
        return obj.group.name
    group_name.short_description = 'Group'

    def teacher_name(self, obj):
        return obj.teacher.user.get_full_name() if obj.teacher and obj.teacher.user else '-'
    teacher_name.short_description = 'Teacher'


@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ('homework_title', 'student_name', 'submitted_at', 'score', 'checked_by')
    search_fields = ('homework__title', 'student__user__first_name', 'student__user__last_name')
    list_filter = ('homework', 'submitted_at')
    ordering = ('-submitted_at',)

    def homework_title(self, obj):
        return obj.homework.title
    homework_title.short_description = 'Homework'

    def student_name(self, obj):
        return obj.student.user.get_full_name()
    student_name.short_description = 'Student'


admin.site.register(LessonSchedule)