# courses/admin.py
from django.contrib import admin
from .models import Course, Group, Material


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'price', 'duration_weeks', 'is_active')
    list_filter = ('level', 'is_active')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'teacher', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'course')
    search_fields = ('name', 'course__title')
    filter_horizontal = ('students',)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'group', 'uploaded_by', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('course',)
