from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()


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