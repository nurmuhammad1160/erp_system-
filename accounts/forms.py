# accounts/forms.py
"""
User Registration va Authentication Forms
"""
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    """
    Yangi foydalanuvchini ro'yxatdan o'tkazish
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
        fields = ['email', 'first_name', 'last_name', 'phone', 'type']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email (masalan: user@example.com)',
                'required': True
            }),
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
            'type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Registration qilayotganda SUPERUSER type ko'rinmasin
        choices = list(self.fields['type'].choices)
        choices = [c for c in choices if c[0] != 'super_user']
        self.fields['type'].choices = choices
    
    def clean_email(self):
        """Email unikalligi tekshirish"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return email
    
    def clean_password1(self):
        """Parol kuchini tekshirish"""
        password1 = self.cleaned_data.get('password1')
        
        if password1:
            try:
                validate_password(password1)
            except ValidationError as e:
                raise ValidationError(str(e))
        
        return password1
    
    def clean(self):
        """Parollarning mos-kelishini tekshirish"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Parollar bir-biriga mos kelmadi.")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Parolni xesh qilib saqlash"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
        
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