# academics/forms.py
"""
Academics Forms - Homework, Attendance, Submissions
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Homework, Attendance, HomeworkSubmission
from courses.models import Group


class HomeworkForm(forms.ModelForm):
    """
    Yangi topshiriq yaratish formasі
    """
    class Meta:
        model = Homework
        fields = ['group', 'title', 'description', 'deadline']
        widgets = {
            'group': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Guruh tanlang'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Topshiriq sarlavhasi',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Topshiriq tavsifi',
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
        }
    
    def clean_title(self):
        """Topshiriq sarlavhasini tekshirish"""
        title = self.cleaned_data.get('title')
        if title and len(title) < 3:
            raise ValidationError("Sarlavaha kamida 3 belgidan iborat bo'lishi kerak.")
        return title
    
    def clean_deadline(self):
        """Deadline ni tekshirish"""
        from django.utils import timezone
        deadline = self.cleaned_data.get('deadline')
        
        if deadline and deadline <= timezone.now():
            raise ValidationError("Deadline hozirgi vaqtdan keyin bo'lishi kerak.")
        
        return deadline


class AttendanceCreateForm(forms.ModelForm):
    """
    Davomat qayd qilish formasі
    """
    class Meta:
        model = Attendance
        fields = ['group', 'student', 'date', 'status']
        widgets = {
            'group': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Guruh tanlang',
                'required': True
            }),
            'student': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Talaba tanlang',
                'required': True
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
        }
    
    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # O'qituvchining faqat o'z guruhlarini ko'rish
        if teacher:
            self.fields['group'].queryset = Group.objects.filter(
                teacher=teacher
            )
    
    def clean(self):
        """Group va student mos-kelishini tekshirish"""
        cleaned_data = super().clean()
        group = cleaned_data.get('group')
        student = cleaned_data.get('student')
        
        if group and student:
            if not group.students.filter(id=student.id).exists():
                raise ValidationError(
                    "Tanlab olgan talaba ushbu guruhda yo'q."
                )
        
        return cleaned_data


class SubmissionCheckForm(forms.ModelForm):
    """
    Topshiriq baholash formasі
    """
    class Meta:
        model = HomeworkSubmission
        fields = ['score', 'feedback']
        widgets = {
            'score': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': 0,
                'max': 100,
                'step': 0.5,
                'placeholder': 'Ball kiriting (0-100)',
                'required': True
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Fikr-mulohaza va tushuntirish',
            }),
        }
    
    def clean_score(self):
        """Ball ni tekshirish"""
        score = self.cleaned_data.get('score')
        
        if score is not None:
            if score < 0 or score > 100:
                raise ValidationError("Ball 0 dan 100 gacha bo'lishi kerak.")
        
        return score


class HomeworkSubmissionForm(forms.ModelForm):
    """
    Topshiriq yuborish formasі (o'quvchi uchun)
    """
    class Meta:
        model = HomeworkSubmission
        fields = ['file', 'text']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': '.pdf,.doc,.docx,.txt,.zip',
                'help_text': 'Maksimal fayl hajmi: 10 MB'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Topshiriqni bu yerga yozishingiz mumkin...',
            }),
        }
    
    def clean(self):
        """File yoki text ko'p bo'lishi shart"""
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        text = cleaned_data.get('text')
        
        if not file and not text:
            raise ValidationError(
                "Topshiriqni fayl orqali yoki matni ko'rinishida yuborishingiz kerak."
            )
        
        return cleaned_data
    
    def clean_file(self):
        """Fayl hajmini tekshirish"""
        file = self.cleaned_data.get('file')
        
        if file:
            # Maksimal 10 MB
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("Fayl hajmi 10 MB dan oshmasligi kerak.")
        
        return file