# academics/urls_student.py
"""
Student URLs - O'quvchi panel
"""
from django.urls import path
from .views import (
    StudentDashboardView,
    StudentCourseListView,
    StudentGradesListView,
    StudentHomeworkDetailView,
    StudentProfileView,
)

app_name = 'student'

urlpatterns = [
    # Dashboard
    path('dashboard/', StudentDashboardView.as_view(), name='dashboard'),
    
    # Courses
    path('courses/', StudentCourseListView.as_view(), name='courses'),
    
    # Grades
    path('grades/', StudentGradesListView.as_view(), name='grades'),
    
    # Homework
    path('homework/<int:pk>/', StudentHomeworkDetailView.as_view(), name='homework'),
    
    # Profile
    path('profile/', StudentProfileView.as_view(), name='profile'),
]
