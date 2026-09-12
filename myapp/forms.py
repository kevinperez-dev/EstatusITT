"""
Archivo: forms.py
Propósito: Define los formularios personalizados utilizados en la aplicación, incluyendo autenticación, creación de usuarios y restablecimiento de contraseñas.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario de creación de usuarios personalizado que incluye campos adicionales:
    - carrera
    - nivel educativo
    """
    carrera = forms.ChoiceField(choices=CustomUser.CARRERA_CHOICES)
    nivel_educativo = forms.ChoiceField(choices=CustomUser.NIVEL_EDUCATIVO_CHOICES)    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name','carrera', 'nivel_educativo', 'password1', 'password2','email']

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class VerifyUserForm(forms.Form):
    """
    Formulario para verificar si un usuario existe basado en el nombre de usuario y correo.
    """
    username = forms.CharField(label="Número de Control", max_length=150)
    email = forms.EmailField(label="Correo Electrónico")

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        user_model = get_user_model()
        if not user_model.objects.filter(username=username, email=email).exists():
            raise forms.ValidationError("No se encontró un usuario con ese nombre de usuario y correo.")
        return cleaned_data
    
class ResetPasswordForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label="Nombre de usuario")
    email = forms.EmailField(required=True, label="Correo electrónico")
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Nueva contraseña",
        min_length=8,
    )
