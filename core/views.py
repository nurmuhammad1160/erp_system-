from django.views.generic import TemplateView
from accounts.mixins import StudentRequiredMixin, TeacherRequiredMixin #, AdminRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from accounts.models import User 

class StudentDashboardView(StudentRequiredMixin, TemplateView):
    template_name = 'student/dashboard.html'

class TeacherDashboardView(TeacherRequiredMixin, TemplateView):
    template_name = 'teacher/dashboard.html'

class AdminDashboardView(TemplateView): 
    template_name = 'admin/dashboard.html' 


def get_dashboard_url(user):

    if user.is_superuser or user.type == User.UserType.MANAGER or user.type == User.UserType.ADMIN:
        return reverse_lazy('admin_dashboard')
    elif user.type == User.UserType.TEACHER or user.type == User.UserType.SUPPORT_TEACHER:
        return reverse_lazy('teacher_dashboard')
    elif user.type == User.UserType.STUDENT:
        return reverse_lazy('student_dashboard')
    
    return reverse_lazy('login') 


def custom_login_redirect(request):
    """Foydalanuvchi tizimga kirgandan keyin chaqiriladigan funksiya"""
    if request.user.is_authenticated:
        return redirect(get_dashboard_url(request.user))
    return redirect(reverse_lazy('login'))


class IndexView(TemplateView):
    template_name = 'common/index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return custom_login_redirect(request)
        return super().dispatch(request, *args, **kwargs)