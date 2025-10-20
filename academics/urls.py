from django.urls import path
from . import views

app_name = "student"   # so we can use {% url 'student:dashboard' %} in templates

urlpatterns = [
    #student urls 
    path("", views.DashboardView.as_view(), name="dashboard"),             # /student/
    path("courses/", views.CoursesView.as_view(), name="courses"),         # /student/courses/
    path("grades/", views.GradesView.as_view(), name="grades"),            # /student/grades/
    path("homework/<int:pk>/", views.HomeworkView.as_view(), name="homework"),  # /student/homework/5/
    path("profile/", views.ProfileView.as_view(), name="profile"),         # /student/profile/
]