# erp_system/urls.py
from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('student/', include('academics.urls')),
    path('admin/', admin.site.urls),
    
    path('auth/', include('accounts.urls')),
    
    path('', include('core.urls')), 
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# path('api/', include('api.urls')), # Kelajakda API uchun
#<<<<<<< HEAD>>>>>>> a29fb977a5829ec732df702013b2b1fca7ed585a
