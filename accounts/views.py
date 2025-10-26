# accounts/views.py
"""
Authentication Views - Production Ready
Login, Register, Logout, Profile
"""
import logging
from django.views.generic import CreateView, TemplateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm
from .mixins import get_dashboard_url

User = get_user_model()
logger = logging.getLogger(__name__)


# ============================================================================
# HOME VIEW
# ============================================================================


class HomeView(TemplateView):
    """
    Bosh sahifa - HAMMA UCHUN home.html
    Hech kim dashboard ga yo'nalmasin!
    """
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ERP Sistema - Bosh Sahifa'
        return context


# ============================================================================
# REGISTER VIEW
# ============================================================================

class RegisterView(SuccessMessageMixin, CreateView):
    """
    Yangi foydalanuvchini ro'yxatdan o'tkazish.
    """
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    success_message = "Ro'yxatdan o'tish muvaffaqiyatli! Tizimga kirishingiz mumkin."
    
    def dispatch(self, request, *args, **kwargs):
        """Login qilgan foydalanuvchi qayta register qila olmaydi."""
        if request.user.is_authenticated:
            return redirect(get_dashboard_url(request.user))
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        logger.info(
            f"Yangi user registratsiya: {user.email} ({user.type})",
            extra={'user_id': user.id, 'email': user.email}
        )
        return response
    
    def form_invalid(self, form):
        logger.warning(
            f"Registration xatosi: {form.errors}",
            extra={'errors': str(form.errors)}
        )
        messages.error(
            self.request,
            "Ro'yxatdan o'tishda xatolik. Iltimos, tekshiring."
        )
        return super().form_invalid(form)


# ============================================================================
# LOGIN VIEW
# ============================================================================

@method_decorator(csrf_protect, name='dispatch')
class CustomLoginView(SuccessMessageMixin, LoginView):
    """
    Custom Login - Rol asosida dashboard ga yo'naltirish.
    """
    template_name = 'accounts/login.html'
    success_message = "Tizimga muvaffaqiyatli kiridingiz!"
    
    def get_success_url(self):
        """Login muvaffaqiyatli bo'lgandan so'ng dashboard ga yo'naltirish."""
        user = self.request.user
        dashboard_url = get_dashboard_url(user)
        
        logger.info(
            f"User login: {user.email} ({user.type})",
            extra={'user_id': user.id, 'email': user.email, 'user_type': user.type}
        )
        return dashboard_url
    
    def dispatch(self, request, *args, **kwargs):
        """Login qilgan foydalanuvchi qayta login qila olmaydi."""
        if request.user.is_authenticated:
            return redirect(get_dashboard_url(request.user))
        return super().dispatch(request, *args, **kwargs)
    
    def form_invalid(self, form):
        """Login xatosi."""
        logger.warning(
            f"Login xatosi - Invalid credentials",
            extra={'errors': str(form.errors)}
        )
        messages.error(
            self.request,
            "Email yoki parol noto'g'ri. Qayta urinib ko'ring."
        )
        return super().form_invalid(form)


# ============================================================================
# LOGOUT VIEW
# ============================================================================


class CustomLogoutView(LogoutView):
    """
    Custom Logout - GET request uchun tasdiqlash sahifasi ko'rsatadi.
    """
    next_page = reverse_lazy('home')
    template_name = 'accounts/logout_confirm.html'
    http_method_names = ['get', 'post']  # ✅ GET va POST ga ruxsat
    
    def get(self, request, *args, **kwargs):
        """GET request - Tasdiqlash sahifasini ko'rsatish"""
        if not request.user.is_authenticated:
            # Agar user login qilmagan bo'lsa, home ga yo'naltirish
            messages.info(request, "Siz allaqachon tizimdan chiqqansiz.")
            return redirect('home')
        
        # Tasdiqlash sahifasini ko'rsatish
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        """POST request - Logout qilish"""
        if request.user.is_authenticated:
            logger.info(
                f"User logout: {request.user.email}",
                extra={'user_id': request.user.id}
            )
        
        # Logout qilish
        return super().post(request, *args, **kwargs)


# ============================================================================
# PROFILE VIEW
# ============================================================================

class ProfileView(LoginRequiredMixin, DetailView):
    """
    Foydalanuvchining profili ko'rish.
    """
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    login_url = reverse_lazy('accounts:login')
    
    def get_object(self):
        """Faqat o'zining profilini ko'rish."""
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Role asosida profil ma'lumotlarini qaytarish
        profile_data = None
        
        try:
            if user.type == 'student':
                profile_data = user.student_profile
            elif user.type == 'teacher':
                profile_data = user.teacher_profile
            elif user.type in ['admin', 'manager']:
                profile_data = user.admin_profile
        except Exception as e:
            logger.warning(
                f"Profile yuklashda xatolik: {str(e)}",
                extra={'user_id': user.id}
            )
            profile_data = None
        
        context['user'] = user
        context['profile'] = profile_data
        context['user_type_display'] = user.get_type_display()
        
        return context


# ============================================================================
# ERROR HANDLERS
# ============================================================================

def handler_404(request, exception=None):
    """404 - Sahifa topilmadi."""
    logger.warning(
        f"404 Error: {request.path}",
        extra={'path': request.path}
    )
    messages.error(request, "Sahifa topilmadi.")
    return redirect('home')


def handler_500(request):
    """500 - Server xatosi."""
    logger.error(
        f"500 Error: {request.path}",
        extra={'path': request.path}
    )
    messages.error(request, "Server xatosi yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.")
    return redirect('home')


def handler_403(request, exception=None):
    """403 - Ruxsat yo'q."""
    logger.warning(
        f"403 Error: {request.path}",
        extra={'path': request.path}
    )
    if request.user.is_authenticated:
        messages.error(request, "Siz bu sahifaga kirish huquqiga ega emassiz.")
        return redirect(get_dashboard_url(request.user))
    return redirect('accounts:login')