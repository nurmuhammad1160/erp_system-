# accounts/urls.py
from django.urls import path
from .views import RegisterView, CustomLoginView, CustomLogoutView
from django.views.generic import TemplateView 

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),

    # 1. Chiqishni tasdiqlash sahifasi (GET so'rovini qabul qiladi)
    path('logout-confirm/', TemplateView.as_view(template_name='common/logout_confirm.html'), name='logout_confirm'),

    # 2. Haqiqiy tizimdan chiqish funksiyasi (CustomLogoutView faqat POST ni kutadi)
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]