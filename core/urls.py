# core/urls.py
from django.urls import path
from .views import IndexView
from .views import IndexView, StudentDashboardView, TeacherDashboardView, AdminDashboardView 

urlpatterns = [
    path('', IndexView.as_view(), name='index'), 

    path('dashboard/student/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('dashboard/teacher/', TeacherDashboardView.as_view(), name='teacher_dashboard'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    
  
]