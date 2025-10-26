# accounts/urls.py
"""
Authentication URLs
"""
from django.urls import path
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