from django.urls import path
from .views import  dashboard, grades, student_homework, student_profile

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('grades', grades, name='student_grades' ),
    path('homework/<int:pk>/', student_homework, name='student_homework'),
    path('profile', student_profile, name='student_profile'),
]