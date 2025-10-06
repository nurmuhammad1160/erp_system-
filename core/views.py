from django.views.generic import TemplateView
from accounts.mixins import StudentRequiredMixin, TeacherRequiredMixin, AdminRequiredMixin

class StudentDashboardView(StudentRequiredMixin, TemplateView):
    template_name = 'student/dashboard.html'

class TeacherDashboardView(TeacherRequiredMixin, TemplateView):
    template_name = 'teacher/dashboard.html'
