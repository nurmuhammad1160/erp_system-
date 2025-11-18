# accounts/urls.py
"""
Authentication URLs
"""
from django.urls import path
<<<<<<< HEAD
from .views import RegisterView, CustomLoginView, CustomLogoutView, EditProfileView
from django.views.generic import TemplateView 

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),

    # 1. Chiqishni tasdiqlash sahifasi (GET so'rovini qabul qiladi)
    path('logout-confirm/', TemplateView.as_view(template_name='common/logout_confirm.html'), name='logout_confirm'),

    # 2. Haqiqiy tizimdan chiqish funksiyasi (CustomLogoutView faqat POST ni kutadi)
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('edit/', EditProfileView.as_view(), name='edit_profile'),
]
app_name = 'accounts'
=======
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout-confirm/', views.CustomLogoutView.as_view(), name='logout_confirm'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
>>>>>>> main
