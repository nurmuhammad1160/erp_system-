# ============================================================================
# academics/urls_teacher.py
# ============================================================================
"""
Teacher URLs - O'qituvchi panel
"""
from django.urls import path
from .views import (
    TeacherDashboardView,
    HomeworkCreateView,
    CheckedSubmissionsListView,
    UncheckedSubmissionsListView,
    SubmissionUpdateView,
    AttendanceListView,
    AttendanceCreateView,
)

app_name = 'teacher'

urlpatterns = [
    # Dashboard
    path('dashboard/', TeacherDashboardView.as_view(), name='dashboard'),
    
    # Homework Management
    path('homework/create/', HomeworkCreateView.as_view(), name='homework_create'),
    path('homework/scored/', CheckedSubmissionsListView.as_view(), name='scored_homeworks'),
    path('homework/unscored/', UncheckedSubmissionsListView.as_view(), name='unscored_homeworks'),
    path('homework/submissions/<int:submission_id>/edit/', SubmissionUpdateView.as_view(), name='edit_submission'),
    
    # Attendance Management
    path('attendance/', AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/create/', AttendanceCreateView.as_view(), name='attendance_create'),
]