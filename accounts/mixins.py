# accounts/mixins.py (Yangi fayl yaratamiz)
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy

def get_dashboard_url(user):
    if user.is_superuser or user.type == 'manager':
        return reverse_lazy('admin_dashboard')
    elif user.type == 'admin':
        return reverse_lazy('admin_dashboard') 
    elif user.type == 'teacher' or user.type == 'support_teacher':
        return reverse_lazy('teacher_dashboard')
    elif user.type == 'student':
        return reverse_lazy('student_dashboard')
    return reverse_lazy('login')

def custom_login_redirect(request):
    if request.user.is_authenticated:
        return redirect(get_dashboard_url(request.user))
    return redirect(reverse_lazy('login'))


# settings.py da foydalanish
# LOGIN_REDIRECT_URL = 'accounts.mixins.custom_login_redirect' # Agar custom funksiya ishlatsak.
# Yoki login view da get_success_url() metodidan foydalanamiz.




class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.type == self.request.user.UserType.STUDENT or self.request.user.is_superuser)
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect(get_dashboard_url(self.request.user))
        return super().handle_no_permission()

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.type in [
            self.request.user.UserType.TEACHER, 
            self.request.user.UserType.SUPPORT_TEACHER, 
            self.request.user.UserType.ADMIN,
            self.request.user.UserType.MANAGER,
            self.request.user.UserType.SUPERUSER,
        ])