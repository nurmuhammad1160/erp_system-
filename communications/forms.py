# communications/forms.py
"""
Communications Forms - Bildirishnomalar, Xabarlar, Elanlar
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Notification, Message, Announcement
from django.contrib.auth import get_user_model

User = get_user_model()


# ============================================================================
# NOTIFICATION FORMS
# ============================================================================

class NotificationForm(forms.ModelForm):
    """
    Bildirishnoma yuborish formasі (Admin uchun)
    """
    recipient_type = forms.ChoiceField(
        choices=[
            ('all', 'Barcha foydalanuvchilarga'),
            ('students', 'Faqat talabalar'),
            ('teachers', 'Faqat o\'qituvchilar'),
            ('admins', 'Faqat adminlar'),
            ('specific', 'Muayyan foydalanuvchilar'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        label="Kimga yuborish",
    )
    
    specific_users = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '3',
            'placeholder': 'Foydalanuvchilar emailini kiriting (har biri yangi qatorga)',
        }),
        help_text="Agar 'Muayyan foydalanuvchilar' tanlangan bo'lsa, emaillarni kiriting"
    )
    
    class Meta:
        model = Notification
        fields = ['title', 'message']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bildirishnoma sarlavhasi',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '5',
                'placeholder': 'Bildirishnoma matni',
                'required': True
            }),
        }
        labels = {
            'title': 'Sarlavhasi',
            'message': 'Matni',
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        
        if title and len(title) < 3:
            raise ValidationError("Sarlavha kamita 3 belgidan iborat bo'lishi kerak.")
        
        if title and len(title) > 255:
            raise ValidationError("Sarlavha 255 belgidan oshmasligi kerak.")
        
        return title
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        
        if message and len(message) < 10:
            raise ValidationError("Xabar matni kamita 10 belgidan iborat bo'lishi kerak.")
        
        return message
    
    def clean_specific_users(self):
        recipient_type = self.cleaned_data.get('recipient_type')
        specific_users = self.cleaned_data.get('specific_users')
        
        if recipient_type == 'specific' and not specific_users:
            raise ValidationError("Muayyan foydalanuvchilar tanlansa, emaillarni kiriting.")
        
        if specific_users:
            emails = [email.strip() for email in specific_users.split('\n') if email.strip()]
            if not emails:
                raise ValidationError("Hech qanday to'g'ri email topilmadi.")
            
            # Email validatsiyasi
            from django.core.validators import validate_email
            for email in emails:
                try:
                    validate_email(email)
                except ValidationError:
                    raise ValidationError(f"'{email}' - to'g'ri email emas.")
        
        return specific_users


class NotificationFilterForm(forms.Form):
    """
    Bildirishnomalarni filtrlash formasі
    """
    READ_CHOICES = [
        ('', '--- Barcha ---'),
        ('read', 'O\'qilgan'),
        ('unread', 'O\'qilmagan'),
    ]
    
    is_read = forms.ChoiceField(
        choices=READ_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sarlavha bo\'ylab qidirish...'
        })
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )


# ============================================================================
# MESSAGE FORMS (Agar Message modeli bo'lsa)
# ============================================================================

class MessageForm(forms.ModelForm):
    """
    Shaxsiy xabar yuborish formasі
    """
    recipient_email = forms.CharField(
        max_length=255,
        label="Qabul qiluvchi email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Qabul qiluvchining emailni kiriting',
            'required': True,
            'autofocus': True
        })
    )
    
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Xabardagi mavzu',
                'required': True
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '5',
                'placeholder': 'Xabardagi matn',
                'required': True
            }),
        }
        labels = {
            'subject': 'Mavzu',
            'body': 'Matn',
        }
    
    def clean_recipient_email(self):
        email = self.cleaned_data.get('recipient_email')
        
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(
                f"Email '{email}' bo'ylab foydalanuvchi topilmadi."
            )
        
        return email
    
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        
        if subject and len(subject) < 3:
            raise ValidationError("Mavzu kamita 3 belgidan iborat bo'lishi kerak.")
        
        return subject
    
    def clean_body(self):
        body = self.cleaned_data.get('body')
        
        if body and len(body) < 10:
            raise ValidationError("Xabar matni kamita 10 belgidan iborat bo'lishi kerak.")
        
        return body


class MessageReplyForm(forms.Form):
    """
    Xabarni javob berish formasі
    """
    body = forms.CharField(
        label="Javob",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '4',
            'placeholder': 'Javobni yozing...',
            'required': True
        })
    )
    
    def clean_body(self):
        body = self.cleaned_data.get('body')
        
        if body and len(body) < 3:
            raise ValidationError("Javob kamita 3 belgidan iborat bo'lishi kerak.")
        
        return body


# ============================================================================
# ANNOUNCEMENT FORMS (Agar Announcement modeli bo'lsa)
# ============================================================================

class AnnouncementForm(forms.ModelForm):
    """
    Umumiy elan yaratish formasі (Admin/Teacher uchun)
    """
    
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'target_audience', 'expires_at']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Elan sarlavhasi',
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '5',
                'placeholder': 'Elan matni',
                'required': True
            }),
            'target_audience': forms.Select(attrs={
                'class': 'form-control',
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }
        labels = {
            'title': 'Sarlavhasi',
            'content': 'Matni',
            'target_audience': 'Maqsadli auditoriya',
            'expires_at': 'Tugash vaqti',
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        
        if title and len(title) < 3:
            raise ValidationError("Sarlavha kamita 3 belgidan iborat bo'lishi kerak.")
        
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        
        if content and len(content) < 10:
            raise ValidationError("Elan matni kamita 10 belgidan iborat bo'lishi kerak.")
        
        return content
    
    def clean(self):
        cleaned_data = super().clean()
        from django.utils import timezone
        
        expires_at = cleaned_data.get('expires_at')
        if expires_at and expires_at <= timezone.now():
            raise ValidationError("Tugash vaqti kelajakda bo'lishi kerak.")
        
        return cleaned_data


class AnnouncementFilterForm(forms.Form):
    """
    Elanlarni filtrlash formasі
    """
    AUDIENCE_CHOICES = [
        ('', '--- Barcha auditoriya ---'),
        ('all', 'Barcha foydalanuvchilar'),
        ('students', 'Talabalar'),
        ('teachers', 'O\'qituvchilar'),
        ('staff', 'Xodimlar'),
    ]
    
    target_audience = forms.ChoiceField(
        choices=AUDIENCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Elan sarlavhasi bo\'ylab qidirish...'
        })
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )


# ============================================================================
# BULK MESSAGE FORM
# ============================================================================

class BulkMessageForm(forms.Form):
    """
    Jami foydalanuvchilarga xabar yuborish formasі
    """
    RECIPIENT_GROUP = [
        ('all', 'Barcha foydalanuvchilar'),
        ('students', 'Barcha talabalar'),
        ('teachers', 'Barcha o\'qituvchilar'),
        ('inactive', 'Faol bo\'lmagan foydalanuvchilar'),
    ]
    
    recipient_group = forms.ChoiceField(
        choices=RECIPIENT_GROUP,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        label="Kimga yuborish",
    )
    
    subject = forms.CharField(
        label="Mavzu",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Xabardagi mavzu',
            'required': True
        })
    )
    
    message = forms.CharField(
        label="Xabar matni",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '5',
            'placeholder': 'Jami foydalanuvchilarga yuboriladi xan xabar',
            'required': True
        })
    )
    
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label="Xabarni barcha foydalanuvchilarga yuborishni tasdiqlayapman"
    )
    
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        
        if subject and len(subject) < 3:
            raise ValidationError("Mavzu kamita 3 belgidan iborat bo'lishi kerak.")
        
        return subject
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        
        if message and len(message) < 10:
            raise ValidationError("Xabar matni kamita 10 belgidan iborat bo'lishi kerak.")
        
        return message