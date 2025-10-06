from django.urls import path
from .views import student_page, student_homework

urlpatterns = [
    path('', student_page, name='student_page'),
    path('homeworks/<int:pk>/', student_homework, name='student_homework'),
]