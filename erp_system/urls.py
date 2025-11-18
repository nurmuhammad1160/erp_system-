# erp_system/urls.py
"""
Main URL Configuration
Barcha applarning URLs bu yerda ro'yxatga olinadi
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import HomeView, handler_404, handler_500, handler_403

# Error handlers
handler404 = 'accounts.views.handler_404'
handler500 = 'accounts.views.handler_500'
handler403 = 'accounts.views.handler_403'

from django.conf.urls.static import static
from . import settings

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    path('student/', include('academics.urls')),
    path('admin/', admin.site.urls),
    
<<<<<<< HEAD
    path('auth/', include('accounts.urls')),
    # also expose accounts under /accounts/ for compatibility with links that expect that path
    path('accounts/', include('accounts.urls')),
=======
    # Home page
    path('', HomeView.as_view(), name='home'),
>>>>>>> main
    
    # Authentication - Login, Register, Logout, Profile
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    
<<<<<<< HEAD
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# path('api/', include('api.urls')), # Kelajakda API uchun
#<<<<<<< HEAD>>>>>>> a29fb977a5829ec732df702013b2b1fca7ed585a
=======
    # Student panel
    path('student/', include(('academics.urls_student', 'student'), namespace='student')),
    
    # Teacher panel
    path('teacher/', include(('academics.urls_teacher', 'teacher'), namespace='teacher')),

    
    # Admin panel
    path('admin-panel/', include(('courses.urls_admin', 'admin_panel'), namespace='admin_panel')),
    
    # Finance - To'lovlar va xarajatlar
    path('finance/', include(('finance.urls', 'finance'), namespace='finance')),
    
    # Communications - Bildirishnomalar
    # path('notifications/', include(('communications.urls', 'communications'), namespace='communications')),
]

# Static va Media files (faqat DEBUG=True bo'lganda)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
>>>>>>> main
