# finance/forms.py
"""
Finance Forms - To'lovlar va Xarajatlar
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Payment, Expense
from accounts.models import StudentProfile


# ============================================================================
# PAYMENT FORMS
# ============================================================================

class PaymentForm(forms.ModelForm):
    """
    To'lov qo'shish formasі (Admin uchun)
    """
    student_email = forms.CharField(
        max_length=255,
        label="Talaba Email",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Talaba email ini kiriting',
            'autofocus': True
        })
    )
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'note']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '0',
                'step': '1000',
                'placeholder': 'To\'lov miqdori (so\'m)',
                'required': True
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control',
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Izoh (ixtiyoriy)',
            }),
        }
    
    def clean_amount(self):
        """To'lov miqdorini tekshirish"""
        amount = self.cleaned_data.get('amount')
        
        if amount and amount <= 0:
            raise ValidationError("To'lov miqdori 0 dan katta bo'lishi kerak.")
        
        return amount
    
    def clean_student_email(self):
        """Talaba mavjudligini tekshirish"""
        email = self.cleaned_data.get('student_email')
        
        try:
            StudentProfile.objects.get(user__email=email)
        except StudentProfile.DoesNotExist:
            raise ValidationError(
                f"Email '{email}' bo'ylab talaba topilmadi. "
                f"Iltimos, to'g'ri email kiriting."
            )
        
        return email
    
    def save(self, commit=True):
        """To'lovni saqlash va talabani bog'lash"""
        instance = super().save(commit=False)
        
        email = self.cleaned_data['student_email']
        student = StudentProfile.objects.get(user__email=email)
        instance.student = student
        
        if commit:
            instance.save()
        
        return instance


class PaymentApproveForm(forms.Form):
    """
    To'lovni tasdiqlash formasі
    """
    approve_reason = forms.CharField(
        required=False,
        label="Tasdiqlash sababi",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '3',
            'placeholder': 'Tasdiqlash sababi (ixtiyoriy)',
        })
    )


class PaymentRejectForm(forms.Form):
    """
    To'lovni rad etish formasі
    """
    reject_reason = forms.CharField(
        required=True,
        label="Rad etish sababi",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '3',
            'placeholder': 'To\'lovni nima uchun rad etayotganingizni yozing',
        })
    )
    
    def clean_reject_reason(self):
        reason = self.cleaned_data.get('reject_reason')
        if reason and len(reason) < 5:
            raise ValidationError("Sabab kamida 5 belgidan iborat bo'lishi kerak.")
        return reason


class PaymentFilterForm(forms.Form):
    """
    To'lovlarni filtrlash formasі
    """
    STATUS_CHOICES = [
        ('', '--- Barcha xolatlar ---'),
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    ]
    
    METHOD_CHOICES = [
        ('', '--- Barcha usullar ---'),
        ('cash', 'Naqad pul'),
        ('card', 'Plastik karta'),
        ('transfer', 'Bank utuvi'),
        ('online', 'Online to\'lov'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=METHOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    start_date = forms.DateField(
        required=False,
        label="Boshlang'ich sana",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    
    end_date = forms.DateField(
        required=False,
        label="Tugash sanasi",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    
    search = forms.CharField(
        required=False,
        label="Talaba qidirish",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Talaba ismi yoki emaili...'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Boshlang'ich sana tugash sanasidan keyin bo'lolmaydi.")
        
        return cleaned_data


# ============================================================================
# EXPENSE FORMS
# ============================================================================

class ExpenseForm(forms.ModelForm):
    """
    Xarajat qo'shish formasі (Admin uchun)
    """
    
    CATEGORY_CHOICES = [
        ('ijara', 'Ijara'),
        ('maoshi', 'Xodimlar maoshi'),
        ('utilities', 'Utilities (elektr, suv, gaz)'),
        ('material', 'Materi va xarajat'),
        ('reklama', 'Reklama'),
        ('transport', 'Transport'),
        ('jihozlar', 'Ofis jihozlari'),
        ('tamirlash', 'Tamirlash va qayta tiklash'),
        ('boshqa', 'Boshqa'),
    ]
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date', 'note']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '0',
                'step': '1000',
                'placeholder': 'Xarajat miqdori (so\'m)',
                'required': True
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Xarajat haqida izoh',
            }),
        }
    
    def clean_amount(self):
        """Xarajat miqdorini tekshirish"""
        amount = self.cleaned_data.get('amount')
        
        if amount and amount <= 0:
            raise ValidationError("Xarajat miqdori 0 dan katta bo'lishi kerak.")
        
        if amount and amount > 1000000000:  # 1 milliard
            raise ValidationError("Xarajat miqdori juda katta.")
        
        return amount
    
    def clean(self):
        cleaned_data = super().clean()
        from django.utils import timezone
        
        date = cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError("Xarajat sanasi kelajakda bo'lolmaydi.")
        
        return cleaned_data


class ExpenseFilterForm(forms.Form):
    """
    Xarajatlarni filtrlash formasі
    """
    CATEGORY_CHOICES = [
        ('', '--- Barcha kategoriyalar ---'),
        ('ijara', 'Ijara'),
        ('maoshi', 'Xodimlar maoshi'),
        ('utilities', 'Utilities'),
        ('material', 'Materi va xarajat'),
        ('reklama', 'Reklama'),
        ('transport', 'Transport'),
        ('jihozlar', 'Ofis jihozlari'),
        ('tamirlash', 'Tamirlash'),
        ('boshqa', 'Boshqa'),
    ]
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        label="Kategoriya",
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    start_date = forms.DateField(
        required=False,
        label="Boshlang'ich sana",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    
    end_date = forms.DateField(
        required=False,
        label="Tugash sanasi",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    
    min_amount = forms.DecimalField(
        required=False,
        decimal_places=0,
        label="Minimal miqdor",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'number',
            'placeholder': 'Minimal miqdor (so\'m)',
        })
    )
    
    max_amount = forms.DecimalField(
        required=False,
        decimal_places=0,
        label="Maksimal miqdor",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'number',
            'placeholder': 'Maksimal miqdor (so\'m)',
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        min_amount = cleaned_data.get('min_amount')
        max_amount = cleaned_data.get('max_amount')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Boshlang'ich sana tugash sanasidan keyin bo'lolmaydi.")
        
        if min_amount and max_amount and min_amount > max_amount:
            raise ValidationError("Minimal miqdor maksimaldan kichik bo'lishi kerak.")
        
        return cleaned_data


class ExpenseBulkUploadForm(forms.Form):
    """
    Xarajatlarni fayldan yuklash (CSV yoki Excel)
    """
    file = forms.FileField(
        label="Xarajatlar fayli",
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'accept': '.csv,.xlsx',
            'required': True
        }),
        help_text="CSV yoki Excel formatida (category, amount, date, note)"
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if file:
            # Fayl turini tekshirish
            if not file.name.endswith(('.csv', '.xlsx')):
                raise ValidationError(
                    "Faqat CSV yoki Excel (.xlsx) formatida fayllar qabul qilinadi."
                )
            
            # Fayl hajmini tekshirish (maks 5 MB)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError("Fayl hajmi 5 MB dan oshmasligi kerak.")
        
        return file