# academics/urls_admin.py
"""
Admin Panel URLs - To'liq boshqaruv tizimi
"""
from django.urls import path
from .views import (
    # Dashboard
    AdminDashboardView,
    
    # User Management
    AdminUserListView,
    AdminUserCreateView,
    AdminUserDetailView,
    AdminUserEditView,
    AdminUserDeleteView,
    AdminUserBulkActionView,
    
    # Course Management
    AdminCourseListView,
    AdminCourseCreateView,
    AdminCourseDetailView,
    AdminCourseEditView,
    AdminCourseDeleteView,
    
    # Group Management
    AdminGroupListView,
    AdminGroupCreateView,
    AdminGroupDetailView,
    AdminGroupEditView,
    AdminGroupDeleteView,
    AdminGroupEnrollView,
    AdminGroupRemoveStudentView,
    
    # Reports
    AdminReportsView,
    AdminExportView,
)

app_name = 'admin'

urlpatterns = [
    
    # ========================================
    # DASHBOARD
    # ========================================
    path('dashboard/', AdminDashboardView.as_view(), name='dashboard'),
    
    # ========================================
    # USER MANAGEMENT
    # ========================================
    path('users/', AdminUserListView.as_view(), name='user_list'),
    path('users/create/', AdminUserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/', AdminUserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', AdminUserEditView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', AdminUserDeleteView.as_view(), name='user_delete'),
    path('users/bulk-action/', AdminUserBulkActionView.as_view(), name='user_bulk'),
    
    # ========================================
    # COURSE MANAGEMENT
    # ========================================
    path('courses/', AdminCourseListView.as_view(), name='course_list'),
    path('courses/create/', AdminCourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/', AdminCourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:pk>/edit/', AdminCourseEditView.as_view(), name='course_edit'),
    path('courses/<int:pk>/delete/', AdminCourseDeleteView.as_view(), name='course_delete'),
    
    # ========================================
    # GROUP MANAGEMENT
    # ========================================
    path('groups/', AdminGroupListView.as_view(), name='group_list'),
    path('groups/create/', AdminGroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/', AdminGroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/edit/', AdminGroupEditView.as_view(), name='group_edit'),
    path('groups/<int:pk>/delete/', AdminGroupDeleteView.as_view(), name='group_delete'),
    path('groups/<int:pk>/enroll/', AdminGroupEnrollView.as_view(), name='group_enroll'),
    path('groups/<int:group_pk>/remove/<int:student_pk>/', 
         AdminGroupRemoveStudentView.as_view(), name='group_remove_student'),
    
    # ========================================
    # REPORTS & ANALYTICS
    # ========================================
    path('reports/', AdminReportsView.as_view(), name='reports'),
    path('reports/export/<str:export_type>/', AdminExportView.as_view(), name='export'),
]