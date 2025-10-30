# academics/urls_teacher.py - BARCHA MUMKIN BO'LGAN URL'LAR
"""
Teacher URLs - O'qituvchi panel
TO'LIQ VERSIYA - Barcha kerakli URL'lar
"""
from django.urls import path
from .views import (
    # Dashboard
    TeacherDashboardView,
    
    # Groups
    GroupsListView,
    GroupDetailView,
    
    # Homework
    HomeworkCreateView,
    HomeworkListView,
    CheckedSubmissionsListView,
    UncheckedSubmissionsListView,
    SubmissionUpdateView,
    
    # Attendance
    AttendanceListView,
    AttendanceCreateView,
    
    # Materials
    MaterialsListView,
    MaterialUploadView,
    
    # Students
    StudentsListView,
    
    # Grades
    GradesListView,
    
    # Schedule - YANGI
    ScheduleView,
    
    # Reports - YANGI
    ReportsView,
    
    # Profile
    TeacherProfileView,
)

app_name = 'teacher'

urlpatterns = [
    # ========================================
    # DASHBOARD
    # ========================================
    path('dashboard/', TeacherDashboardView.as_view(), name='dashboard'),
    
    # ========================================
    # PROFILE
    # ========================================
    path('profile/', TeacherProfileView.as_view(), name='profile'),
    
    # ========================================
    # GROUPS
    # ========================================
    path('groups/', GroupsListView.as_view(), name='groups'),
    path('groups/<int:pk>/', GroupDetailView.as_view(), name='group_detail'),
    
    # ========================================
    # HOMEWORK
    # ========================================
    path('homework/', HomeworkListView.as_view(), name='homework_list'),
    path('homework/create/', HomeworkCreateView.as_view(), name='homework_create'),
    path('homework/scored/', CheckedSubmissionsListView.as_view(), name='scored_homeworks'),
    path('homework/unscored/', UncheckedSubmissionsListView.as_view(), name='unscored_homeworks'),
    path('homework/submissions/<int:submission_id>/edit/', SubmissionUpdateView.as_view(), name='edit_submission'),
    
    # ========================================
    # ATTENDANCE
    # ========================================
    path('attendance/', AttendanceListView.as_view(), name='attendance'),
    path('attendance/list/', AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/create/', AttendanceCreateView.as_view(), name='attendance_create'),
    
    # ========================================
    # SCHEDULE (Dars jadvali)
    # ========================================
    path('schedule/', ScheduleView.as_view(), name='schedule'),
    
    # ========================================
    # MATERIALS
    # ========================================
    path('materials/', MaterialsListView.as_view(), name='materials'),
    path('materials/upload/', MaterialUploadView.as_view(), name='material_upload'),
    
    # ========================================
    # STUDENTS
    # ========================================
    path('students/', StudentsListView.as_view(), name='students'),
    path('students/list/', StudentsListView.as_view(), name='students_list'),
    
    # ========================================
    # GRADES
    # ========================================
    path('grades/', GradesListView.as_view(), name='grades'),
    path('grades/list/', GradesListView.as_view(), name='grades_list'),
    
    # ========================================
    # REPORTS
    # ========================================
    path('reports/', ReportsView.as_view(), name='reports'),
]