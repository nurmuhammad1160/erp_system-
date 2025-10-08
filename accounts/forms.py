from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Parol")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Parolni takrorlang")

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'password')

    def clean_email(self):
        """Email manzilini mustahkam regex orqali tekshirish"""
        email = self.cleaned_data.get('email')
        
        
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.fullmatch(regex, email):
            raise ValidationError("Email manzili to'g'ri formatda emas. Iltimos, tekshiring.")
        
        if User.objects.filter(email=email).exists():
             raise ValidationError("Bu email manzilidan avval ro'yxatdan o'tilgan.")

        return email

    def clean(self):
        """Parollar mosligini va murakkabligini tekshirish"""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError(
                "Kiritilgan parollar bir xil emas."
            )

    
        if password:
            if len(password) < 8:
                raise forms.ValidationError("Parol kamida 8 ta belgidan iborat bo'lishi kerak.")
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError("Parolda kamida bitta bosh harf bo'lishi shart.")
            if not re.search(r'[a-z]', password):
                raise forms.ValidationError("Parolda kamida bitta kichik harf bo'lishi shart.")
            if not re.search(r'[0-9]', password):
                raise forms.ValidationError("Parolda kamida bitta raqam bo'lishi shart.")
            # if not re.search(r'[!@#$%^&*()]', password):
            #     raise forms.ValidationError("Parolda kamida bitta maxsus belgi bo'lishi shart.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.type = User.UserType.STUDENT 
        if commit:
            user.save()
        return user