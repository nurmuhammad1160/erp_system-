from django import forms
from .models import Homework, HomeworkSubmission, Attendance

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['title', 'description', 'deadline', 'group']
