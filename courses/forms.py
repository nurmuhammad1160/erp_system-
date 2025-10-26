# courses/forms.py
"""
Courses Forms - Kurslar, Guruhlar, Materiallar
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Course, Group, Material


# ============================================================================
# COURSE FORMS
# ============================================================================

class CourseForm(forms.ModelForm):
    """
    Yangi kurs yaratish formasі
    """
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'duration_weeks', 'level', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kurs nomi (masalan: Python Asoslari)',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '5',
                'placeholder': 'Kurs tavsifi - nima o\'rgatiladi, qanday foydali, va h.k',
                'required': True
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '0',
                'step': '10000',
                'placeholder': 'Kurs narxi (so\'m)',
                'required': True
            }),
            'duration_weeks': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '1',
                'max': '52',
                'placeholder': 'Kurs davomiyligi (haftalar)',
                'required': True
            }),
            'level': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'title': 'Kurs nomi',
            'description': 'Tavsifi',
            'price': 'Narxi (so\'m)',
            'duration_weeks': 'Davomiyligi (haftalar)',
            'level': 'Darajasi',
            'is_active': 'Faol qilish',
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        
        if title and len(title) < 3:
            raise ValidationError("Kurs nomi kamita 3 belgidan iborat bo'lishi kerak.")
        
        # Duplikat tekshirish
        if title and Course.objects.filter(title__iexact=title).exclude(id=self.instance.id).exists():
            raise ValidationError("Bu nomli kurs allaqachon mavjud.")
        
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        
        if description and len(description) < 20:
            raise ValidationError("Tavsif kamita 20 belgidan iborat bo'lishi kerak.")
        
        return description
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        
        if price and price < 0:
            raise ValidationError("Narx manfiy bo'lolmaydi.")
        
        return price
    
    def clean_duration_weeks(self):
        duration = self.cleaned_data.get('duration_weeks')
        
        if duration and (duration < 1 or duration > 52):
            raise ValidationError("Davomiyligi 1 dan 52 haftagacha bo'lishi kerak.")
        
        return duration


class CourseUpdateForm(CourseForm):
    """
    Kursni tahrirlash formasі
    """
    pass


# ============================================================================
# GROUP FORMS
# ============================================================================

class GroupForm(forms.ModelForm):
    """
    Yangi guruh yaratish formasі
    """
    class Meta:
        model = Group
        fields = ['name', 'course', 'teacher', 'support_teacher', 'start_date', 'end_date', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Guruh nomi (masalan: A1, B2, va h.k)',
                'required': True
            }),
            'course': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'teacher': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'support_teacher': forms.Select(attrs={
                'class': 'form-control',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
        }
        labels = {
            'name': 'Guruh nomi',
            'course': 'Kurs',
            'teacher': 'O\'qituvchi',
            'support_teacher': 'Qo\'shimcha o\'qituvchi',
            'start_date': 'Boshlash sanasi',
            'end_date': 'Tugash sanasi',
            'status': 'Holatı',
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        
        if name and len(name) < 2:
            raise ValidationError("Guruh nomi kamita 2 belgidan iborat bo'lishi kerak.")
        
        return name
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        course = cleaned_data.get('course')
        
        # Sanalarni tekshirish
        if start_date and end_date:
            if start_date >= end_date:
                raise ValidationError("Boshlash sanasi tugash sanasidan oldin bo'lishi kerak.")
            
            # Davomiyligi tekshirish
            delta = (end_date - start_date).days
            if course:
                expected_days = course.duration_weeks * 7
                if delta < expected_days:
                    raise ValidationError(
                        f"Guruh davomiyligi kurs davomiyligi ({course.duration_weeks} haftada) "
                        f"ga mos bo'lishi kerak. Hozirda {delta // 7} haftaga o'rnatilgan."
                    )
        
        return cleaned_data


class GroupUpdateForm(GroupForm):
    """
    Guruhni tahrirlash formasі
    """
    pass


class GroupAddStudentsForm(forms.Form):
    """
    Guruhga talabalarni qo'shish formasі
    """
    students = forms.CharField(
        label="Talabaları qo'shish",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '5',
            'placeholder': 'Talabaları emaillar bo\'ylab kiriting (har biri yangi qatorga). '
                          'Masalan:\nstudent1@example.com\nstudent2@example.com',
        }),
        help_text="Talabaları emaillar bo'ylab kiriting, har biri yangi qatorga"
    )
    
    def clean_students(self):
        students_text = self.cleaned_data.get('students')
        
        if not students_text:
            raise ValidationError("Kamita bir talaba email ini kiriting.")
        
        # Email larni ajratish
        emails = [email.strip() for email in students_text.split('\n') if email.strip()]
        
        if not emails:
            raise ValidationError("Hech qanday to'g'ri email topilmadi.")
        
        # Email validatsiyasi
        from django.core.validators import validate_email
        for email in emails:
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError(f"'{email}' - to'g'ri email emas.")
        
        return emails


class GroupFilterForm(forms.Form):
    """
    Guruhlarni filtrlash formasі
    """
    STATUS_CHOICES = [
        ('', '--- Barcha xolatlar ---'),
        ('active', 'Faol'),
        ('finished', 'Tugallanish'),
        ('archived', 'Arxivlangan'),
    ]
    
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        empty_label="--- Barcha kurslar ---",
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Guruh nomi bo\'ylab qidirish...'
        })
    )


# ============================================================================
# MATERIAL FORMS
# ============================================================================

class MaterialForm(forms.ModelForm):
    """
    Dars materiali yuklash formasі
    """
    class Meta:
        model = Material
        fields = ['title', 'description', 'file', 'course', 'group']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Material nomi (masalan: Dars 1 - Kirish)',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Material tavsifi (nima qo\'shilganini yozing)',
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': '.pdf,.doc,.docx,.ppt,.pptx,.zip,.txt,.xlsx',
            }),
            'course': forms.Select(attrs={
                'class': 'form-control',
            }),
            'group': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'title': 'Material nomi',
            'description': 'Tavsifi',
            'file': 'Fayl yuklash',
            'course': 'Kurs',
            'group': 'Guruh (ixtiyoriy)',
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        
        if title and len(title) < 3:
            raise ValidationError("Material nomi kamita 3 belgidan iborat bo'lishi kerak.")
        
        return title
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if file:
            # Fayl turini tekshirish
            allowed_extensions = [
                'pdf', 'doc', 'docx', 'ppt', 'pptx', 
                'zip', 'txt', 'xlsx', 'xls', 'csv'
            ]
            
            file_ext = file.name.split('.')[-1].lower()
            if file_ext not in allowed_extensions:
                raise ValidationError(
                    f"Fayl turi '{file_ext}' qo'llab-quvvatlanmaydi. "
                    f"Ruxsat etilgan turlar: {', '.join(allowed_extensions)}"
                )
            
            # Fayl hajmini tekshirish (maks 50 MB)
            if file.size > 50 * 1024 * 1024:
                raise ValidationError("Fayl hajmi 50 MB dan oshmasligi kerak.")
        
        return file
    
    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        group = cleaned_data.get('group')
        
        # Group tanlansa, u course ga tegishli bo'lishi kerak
        if group and course:
            if group.course != course:
                raise ValidationError(
                    "Tanlab olgan guruh tanlab olgan kursga tegishli emas."
                )
        
        return cleaned_data


class MaterialFilterForm(forms.Form):
    """
    Materiallarni filtrlash formasі
    """
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        empty_label="--- Barcha kurslar ---",
        label="Kurs",
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        empty_label="--- Barcha guruhlar ---",
        label="Guruh",
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    search = forms.CharField(
        required=False,
        label="Qidirish",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Material nomi bo\'ylab qidirish...'
        })
    )