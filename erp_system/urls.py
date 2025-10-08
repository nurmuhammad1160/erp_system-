# erp_system/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('auth/', include('accounts.urls')),
    
    path('', include('core.urls')), 
    
    # path('api/', include('api.urls')), # Kelajakda API uchun
]