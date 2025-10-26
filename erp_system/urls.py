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

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Home page
    path('', HomeView.as_view(), name='home'),
    
    # Authentication - Login, Register, Logout, Profile
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    
    # Student panel
    path('student/', include(('academics.urls_student', 'student'), namespace='student')),
    
    # Teacher panel
    path('teacher/', include(('academics.urls_teacher', 'teacher'), namespace='teacher')),
    
    # Admin panel
    # path('admin-panel/', include(('courses.urls_admin', 'admin_panel'), namespace='admin_panel')),
    
    # Finance - To'lovlar va xarajatlar
    path('finance/', include(('finance.urls', 'finance'), namespace='finance')),
    
    # Communications - Bildirishnomalar
    # path('notifications/', include(('communications.urls', 'communications'), namespace='communications')),
]

# Static va Media files (faqat DEBUG=True bo'lganda)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)