# accounts/views.py
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm
from core.views import custom_login_redirect, get_dashboard_url 
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect 

class RegisterView(SuccessMessageMixin, CreateView):
    model = get_user_model()
    form_class = UserRegistrationForm
    template_name = 'common/register.html'
    success_url = reverse_lazy('login') # Ro'yxatdan o'tgach, login sahifasiga yo'naltiramiz
    success_message = "Muvaffaqiyatli ro'yxatdan o'tdingiz. Tizimga kirishingiz mumkin."
    
    # Ro'yxatdan o'tgan foydalanuvchini qayta yo'naltirish
    def dispatch(self, request, *args, **kwargs):
        
        if request.user.is_authenticated:
            return custom_login_redirect(request)
        return super().dispatch(request, *args, **kwargs)
    




class CustomLoginView(LoginView):
    template_name = 'common/login.html'

    def get_success_url(self):
        """Login muvaffaqiyatli bo'lgandan so'ng to'g'ri dashboardga yo'naltiramiz"""
        return get_dashboard_url(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """Agar foydalanuvchi allaqachon login qilgan bo'lsa, uni redirect qilish."""
        if request.user.is_authenticated:
            return redirect(get_dashboard_url(request.user)) 
        
        return super().dispatch(request, *args, **kwargs)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
    template_name = 'common/logout_confirm.html' 