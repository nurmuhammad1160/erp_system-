from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    ManagerProfile,
    AdminProfile,
    TeacherProfile,
    SupportTeacherProfile,
    StudentProfile
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin integrated with email authentication"""
    model = User
    list_display = ('email', 'first_name', 'last_name', 'phone', 'type', 'is_staff', 'is_active')
    list_filter = ('type', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined',)

    fieldsets = (
        ('Asosiy maʼlumotlar', {'fields': ('email', 'password')}),
        ('Shaxsiy maʼlumotlar', {'fields': ('first_name', 'last_name', 'phone', 'type')}),
        ('Ruxsatlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Vaqt maʼlumotlari', {'fields': ('date_joined',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'type', 'is_active', 'is_staff'),
        }),
    )


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'branch', 'salary')
    list_filter = ('branch',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'position')


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'manager', 'branch', 'salary')
    list_filter = ('branch',)
    search_fields = ('user__email', 'manager__user__email')


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'speciality', 'salary', 'rating')
    list_filter = ('rating',)
    search_fields = ('user__email', 'speciality')


@admin.register(SupportTeacherProfile)
class SupportTeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'related_teacher')
    search_fields = ('user__email', 'related_teacher__user__email')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'parent_name', 'parent_phone', 'balance', 'status')
    list_filter = ('status',)
    search_fields = ('user__email', 'parent_name', 'parent_phone')
