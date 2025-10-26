# accounts/mixins.py
"""
Role-based access control mixins va permission management
Senior-level security implementation
"""
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.http import Http404
from functools import wraps
from django.contrib import messages


# ============================================================================
# 1. DASHBOARD URL MAPPING - Role asosida yo'naltirish
# ============================================================================

ROLE_DASHBOARD_MAP = {
    'super_user': 'admin:dashboard',
    'manager': 'admin:dashboard',
    'admin': 'admin:dashboard',
    'teacher': 'teacher:dashboard',
    'support_teacher': 'teacher:dashboard',
    'student': 'student:dashboard',
}


def get_dashboard_url(user):
    """
    Foydalanuvchining roliga asosida dashboard URL ni qaytaradi.
    
    Args:
        user: Django User object
    
    Returns:
        str: Dashboard URL
    """
    if not user.is_authenticated:
        return reverse_lazy('accounts:login')
    
    return reverse_lazy(ROLE_DASHBOARD_MAP.get(user.type, 'accounts:login'))


def redirect_to_dashboard(request):
    """
    Login qilgan foydalanuvchini tege'l dashboard ga yo'naltiradi.
    """
    if request.user.is_authenticated:
        return redirect(get_dashboard_url(request.user))
    return redirect(reverse_lazy('accounts:login'))


# ============================================================================
# 2. CUSTOM LOGIN MIXIN - Xavfsiz kirish
# ============================================================================

class CustomLoginRedirectMixin(LoginRequiredMixin):
    """
    Login-required validation va role-based redirection.
    Barcha protected views uchun ishlatilinadi.
    """
    login_url = reverse_lazy('accounts:login')
    
    def handle_no_permission(self):
        """Login qilmagan foydalanuvchi login sahifasiga yo'naltiriladi"""
        messages.warning(self.request, "Iltimos, avval tizimga kiring.")
        return super().handle_no_permission()
    
    def dispatch(self, request, *args, **kwargs):
        """Har bir request da login tekshiriladi"""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# ============================================================================
# 3. ROLE-BASED MIXINS - Rol tekshirish
# ============================================================================

class StudentRequiredMixin(CustomLoginRedirectMixin, UserPassesTestMixin):
    """
    Faqat o'quvchilar uchun access.
    Superuser ham kirishi mumkin.
    """
    permission_denied_message = "Siz o'quvchi bo'lmagani uchun bu sahifaga kira olmaysiz."
    
    def test_func(self):
        """O'quvchi yoki superuser tekshirish"""
        return (self.request.user.type == 'student' or 
                self.request.user.is_superuser)
    
    def handle_no_permission(self):
        """Ruxsat yo'q bo'lsa, o'z dashboardiga yo'naltirish"""
        if self.request.user.is_authenticated:
            messages.error(self.request, self.permission_denied_message)
            return redirect(get_dashboard_url(self.request.user))
        return super().handle_no_permission()


class TeacherRequiredMixin(CustomLoginRedirectMixin, UserPassesTestMixin):
    """
    O'qituvchi, support o'qituvchi va admin uchun access.
    Manager, superuser ham kirishi mumkin.
    """
    permission_denied_message = "Siz o'qituvchi yo'q. Bu sahifaga kirish huquqi yo'q."
    
    def test_func(self):
        """O'qituvchi tipini tekshirish"""
        allowed_types = [
            'teacher',
            'support_teacher',
            'admin',
            'manager',
            'super_user'
        ]
        return self.request.user.type in allowed_types or self.request.user.is_superuser
    
    def handle_no_permission(self):
        """Ruxsat yo'q bo'lsa, o'z dashboardiga yo'naltirish"""
        if self.request.user.is_authenticated:
            messages.error(self.request, self.permission_denied_message)
            return redirect(get_dashboard_url(self.request.user))
        return super().handle_no_permission()


class AdminRequiredMixin(CustomLoginRedirectMixin, UserPassesTestMixin):
    """
    Faqat admin va manager uchun access.
    """
    permission_denied_message = "Siz admin bo'lmagani uchun bu sahifaga kira olmaysiz."
    
    def test_func(self):
        """Admin tekshirish"""
        allowed_types = ['admin', 'manager', 'super_user']
        return self.request.user.type in allowed_types or self.request.user.is_superuser
    
    def handle_no_permission(self):
        """Ruxsat yo'q bo'lsa"""
        if self.request.user.is_authenticated:
            messages.error(self.request, self.permission_denied_message)
            return redirect(get_dashboard_url(self.request.user))
        return super().handle_no_permission()


class ManagerRequiredMixin(CustomLoginRedirectMixin, UserPassesTestMixin):
    """
    Faqat manager va superuser uchun.
    """
    permission_denied_message = "Bu sahifa faqat manager uchun."
    
    def test_func(self):
        return self.request.user.type in ['manager', 'super_user'] or self.request.user.is_superuser
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, self.permission_denied_message)
            return redirect(get_dashboard_url(self.request.user))
        return super().handle_no_permission()


# ============================================================================
# 4. PERMISSION-BASED MIXINS - Granular permissions
# ============================================================================

class PermissionRequiredMixin(CustomLoginRedirectMixin):
    """
    Custom permission tekshiradigan mixin.
    
    Usage:
        class MyView(PermissionRequiredMixin, TemplateView):
            required_permissions = ['can_view_grades']
    """
    required_permissions = []
    permission_denied_message = "Siz bu amaliyotni bajarishga ruxsat yo'q."
    
    def dispatch(self, request, *args, **kwargs):
        """Permission tekshirish"""
        if not self.has_permissions():
            messages.error(request, self.permission_denied_message)
            return redirect(get_dashboard_url(request.user))
        return super().dispatch(request, *args, **kwargs)
    
    def has_permissions(self):
        """User permissions tekshirish"""
        user = self.request.user
        if user.is_superuser or user.type == 'manager':
            return True
        
        for perm in self.required_permissions:
            if not user.has_perm(perm):
                return False
        return True
    
    def get_context_data(self, **kwargs):
        """Context da permissions qo'shish"""
        context = super().get_context_data(**kwargs)
        context['user_permissions'] = self.request.user.get_all_permissions()
        return context


# ============================================================================
# 5. FUNCTION-BASED VIEW DECORATORS - Dekorator asosida tekshirish
# ============================================================================

def student_required(view_func):
    """
    Function-based view uchun student tekshiradigan decorator.
    
    Usage:
        @student_required
        def my_view(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Iltimos, avval tizimga kiring.")
            return redirect(reverse_lazy('accounts:login'))
        
        if request.user.type != 'student' and not request.user.is_superuser:
            messages.error(request, "Siz o'quvchi bo'lmagani uchun bu sahifaga kira olmaysiz.")
            return redirect(get_dashboard_url(request.user))
        
        return view_func(request, *args, **kwargs)
    return wrapper


def teacher_required(view_func):
    """
    Function-based view uchun teacher tekshiradigan decorator.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Iltimos, avval tizimga kiring.")
            return redirect(reverse_lazy('accounts:login'))
        
        allowed_types = ['teacher', 'support_teacher', 'admin', 'manager', 'super_user']
        if request.user.type not in allowed_types and not request.user.is_superuser:
            messages.error(request, "Siz o'qituvchi yo'q.")
            return redirect(get_dashboard_url(request.user))
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """
    Function-based view uchun admin tekshiradigan decorator.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Iltimos, avval tizimga kiring.")
            return redirect(reverse_lazy('accounts:login'))
        
        allowed_types = ['admin', 'manager', 'super_user']
        if request.user.type not in allowed_types and not request.user.is_superuser:
            messages.error(request, "Siz admin bo'lmagani uchun bu sahifaga kira olmaysiz.")
            return redirect(get_dashboard_url(request.user))
        
        return view_func(request, *args, **kwargs)
    return wrapper


def permission_required(*perms):
    """
    Granular permission tekshiradigan decorator.
    
    Usage:
        @permission_required('can_view_grades', 'can_edit_homework')
        def my_view(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Iltimos, avval tizimga kiring.")
                return redirect(reverse_lazy('accounts:login'))
            
            # Superuser va manager - har doim ruxsat
            if request.user.is_superuser or request.user.type == 'manager':
                return view_func(request, *args, **kwargs)
            
            # Permission tekshirish
            for perm in perms:
                if not request.user.has_perm(perm):
                    messages.error(request, "Siz bu amaliyotni bajarishga ruxsat yo'q.")
                    return redirect(get_dashboard_url(request.user))
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# 6. CONTEXT PROCESSOR - Har sahifada rol info
# ============================================================================

def user_context(request):
    """
    Template da user role info qo'shish.
    
    Usage in template:
        {{ user_role }}
        {{ is_student }}
        {{ is_teacher }}
        {{ is_admin }}
    """
    if not request.user.is_authenticated:
        return {}
    
    return {
        'user_role': request.user.get_type_display(),
        'is_student': request.user.type == 'student',
        'is_teacher': request.user.type in ['teacher', 'support_teacher'],
        'is_admin': request.user.type in ['admin', 'manager'],
        'is_superuser': request.user.is_superuser,
    }
