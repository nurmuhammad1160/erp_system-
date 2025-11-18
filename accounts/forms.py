# accounts/forms.py
"""
User Registration va Authentication Forms
"""
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

<<<<<<< HEAD

class StudentProfileForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    phone = forms.CharField(required=False)

    def __init__(self, *args, user=None, student=None, **kwargs):
        # allow editing both User and StudentProfile fields in a single form
        super().__init__(*args, **kwargs)
        self.user = user
        self.student = student
        # Dynamically construct fields
        if user is not None:
            self.fields['first_name'] = forms.CharField(required=False, initial=user.first_name)
            self.fields['last_name'] = forms.CharField(required=False, initial=user.last_name)
            self.fields['email'] = forms.EmailField(required=True, initial=user.email)
            self.fields['phone'] = forms.CharField(required=False, initial=user.phone)
        if student is not None:
            self.fields['parent_name'] = forms.CharField(required=False, initial=student.parent_name)
            self.fields['parent_phone'] = forms.CharField(required=False, initial=student.parent_phone)
            self.fields['avatar'] = forms.ImageField(required=False)
           
    def save(self, commit=True):
        # save user fields
        if self.user is not None:
            self.user.first_name = self.cleaned_data.get('first_name', self.user.first_name)
            self.user.last_name = self.cleaned_data.get('last_name', self.user.last_name)
            self.user.email = self.cleaned_data.get('email', self.user.email)
            self.user.phone = self.cleaned_data.get('phone', self.user.phone)
            if commit:
                self.user.save()

        if self.student is not None:
            self.student.parent_name = self.cleaned_data.get('parent_name', self.student.parent_name)
            self.student.parent_phone = self.cleaned_data.get('parent_phone', self.student.parent_phone)
            # avatar file handling
            avatar = self.cleaned_data.get('avatar')
            if avatar:
                self.student.avatar = avatar
            self.student.status = self.cleaned_data.get('status', self.student.status)
            if commit:
                self.student.save()

        return self.user if self.user is not None else self.student

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Parol")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Parolni takrorlang")
=======
>>>>>>> main

class UserRegistrationForm(forms.ModelForm):
    """
    Yangi foydalanuvchini ro'yxatdan o'tkazish - FIXED VERSION
    
    Features:
    - Default: Student sifatida ro'yxatdan o'tadi
    - Type field yo'q (avtomatik student)
    - Auto StudentProfile yaratish
    - Email lowercase
    - Password strength validation
    - Phone format validation
    """
    
    password1 = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parolni kiriting',
            'autocomplete': 'new-password'
        })
    )
    
    password2 = forms.CharField(
        label="Parolni qayta kiriting",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parolni qayta kiriting',
            'autocomplete': 'new-password'
        })
    )
    
    class Meta:
        model = User
        # TYPE field'ni olib tashladik - default student bo'ladi
        fields = ['email', 'first_name', 'last_name', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ismingiz',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Familiyangiz',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998 90 123 45 67',
            }),
        }
    
    def clean_email(self):
        """
        Email unikalligi va formatini tekshirish
        """
        email = self.cleaned_data.get('email')
        if email:
            # Email lowercase qilib saqlash
            email = email.lower().strip()
            
            # Email unikalligi tekshirish (case-insensitive)
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        
        return email
    
    def clean_phone(self):
        """
        Telefon formatini tekshirish
        """
        phone = self.cleaned_data.get('phone')
        if phone:
            # Bo'sh joylarni olib tashlash
            phone = phone.strip()
            
            # Telefon formatini tekshirish
            if not phone.startswith('+998') and not phone.startswith('998'):
                raise ValidationError("Telefon raqam +998 bilan boshlanishi kerak.")
        
        return phone
    
    def clean_password1(self):
        """
        Parol kuchini tekshirish
        """
        password1 = self.cleaned_data.get('password1')
        
        if password1:
            # Minimum length check
            if len(password1) < 8:
                raise ValidationError("Parol kamida 8 belgidan iborat bo'lishi kerak.")
            
            # Django's built-in password validators
            try:
                validate_password(password1)
            except ValidationError as e:
                # Convert error messages list to string
                raise ValidationError('. '.join(e.messages))
        
        return password1
    
    def clean(self):
        """
        Parollarning mos-kelishini tekshirish
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError({
                    'password2': "Parollar bir-biriga mos kelmadi."
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        """
        User'ni saqlash va StudentProfile yaratish
        
        Features:
        - Password'ni hash qilish
        - Type'ni 'student' qilish
        - Email'ni lowercase qilish
        - StudentProfile avtomatik yaratish
        """
        user = super().save(commit=False)
        
        # Password hash
        user.set_password(self.cleaned_data['password1'])
        
        # DEFAULT: Student type
        user.type = 'student'
        
        # Email lowercase
        user.email = user.email.lower()
        
        if commit:
            user.save()
            
            # Student profile yaratish
            from accounts.models import StudentProfile
            StudentProfile.objects.get_or_create(user=user)
        
        return user


class UserProfileUpdateForm(forms.ModelForm):
    """
    Foydalanuvchi profilini yangilash
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ism',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Familiya',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telefon (+998...)',
            }),
        }


class PasswordChangeForm(forms.Form):
    """
    Parol o'zgartirish formasі
    """
    old_password = forms.CharField(
        label="Eski parol",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Eski parolni kiriting',
            'autocomplete': 'current-password'
        })
    )
    
    new_password1 = forms.CharField(
        label="Yangi parol",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Yangi parolni kiriting',
            'autocomplete': 'new-password'
        })
    )
    
    new_password2 = forms.CharField(
        label="Yangi parolni qayta kiriting",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Yangi parolni qayta kiriting',
            'autocomplete': 'new-password'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        """Eski parol tekshirish"""
        old_password = self.cleaned_data.get('old_password')
        
        if not self.user.check_password(old_password):
            raise ValidationError("Eski parol noto'g'ri.")
        
        return old_password
    
    def clean_new_password1(self):
        """Yangi parol kuchini tekshirish"""
        new_password1 = self.cleaned_data.get('new_password1')
        
        if new_password1:
            try:
                validate_password(new_password1, self.user)
            except ValidationError as e:
                raise ValidationError(str(e))
        
        return new_password1
    
    def clean(self):
        """Parollarning mos-kelishini tekshirish"""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError("Yangi parollar bir-biriga mos kelmadi.")
        
        return cleaned_data
    
    def save(self):
        """Parolni o'zgartirish"""
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user