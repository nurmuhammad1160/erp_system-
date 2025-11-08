# academics/urls_student.py
"""
Student URLs - O'quvchi panel (COMPLETE)
"""
from django.urls import path
from .views import (
    # Dashboard
    StudentDashboardView,
    
    # Homework
    StudentHomeworkListView,
    StudentHomeworkDetailView,
    
    # Grades
    StudentGradesListView,
    
    # Courses
    StudentCourseListView,
    
    # Attendance
    StudentAttendanceHistoryView,
    
    # Profile
    StudentProfileView,
)

app_name = 'student'

urlpatterns = [
    # ========================================
    # DASHBOARD
    # ========================================
    path('dashboard/', StudentDashboardView.as_view(), name='dashboard'),
    
    # ========================================
    # HOMEWORK
    # ========================================
    path('homework/', StudentHomeworkListView.as_view(), name='homework_list'),
    path('homework/<int:pk>/', StudentHomeworkDetailView.as_view(), name='homework_detail'),
    
    # ========================================
    # GRADES
    # ========================================
    path('grades/', StudentGradesListView.as_view(), name='grades'),
    
    # ========================================
    # COURSES
    # ========================================
    path('courses/', StudentCourseListView.as_view(), name='courses'),
    
    # ========================================
    # ATTENDANCE
    # ========================================
    path('attendance/', StudentAttendanceHistoryView.as_view(), name='attendance_history'),
    
    # ========================================
    # PROFILE
    # ========================================
    path('profile/', StudentProfileView.as_view(), name='profile'),
]