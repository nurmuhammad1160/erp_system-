from django.urls import path
from . import views

app_name = "student"   # so we can use {% url 'student:dashboard' %} in templates

urlpatterns = [
    path("", views.dashboard, name="dashboard"),             # /student/
    path("courses/", views.courses, name="courses"),         # /student/courses/
    path("grades/", views.grades, name="grades"),            # /student/grades/
    path("homework/<int:pk>/", views.homework, name="homework"),  # /student/homework/5/
    path("profile/", views.profile, name="profile"),         # /student/profile/
]