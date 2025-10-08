from django.urls import path

import courses
from .views import  dashboard

urlpatterns = [
     path('', dashboard, name='dashboard'),
    # path('grades', grades, name='student_grades' ),
    # path('homework/<int:pk>/', student_homework, name='student_homework'),
    # path('profile', student_profile, name='student_profile'),
    # path('courselist', courseslist, name='courses'),
]