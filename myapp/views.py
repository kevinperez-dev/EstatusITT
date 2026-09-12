from django.http import HttpResponse
from django.shortcuts import render, redirect
import logging
from functools import wraps

from django.contrib.auth import login, update_session_auth_hash
from .forms import CustomUserCreationForm, CustomAuthenticationForm, VerifyUserForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .forms import ResetPasswordForm # Formulario para capturar la nueva contraseña

# Obtiene el modelo de usuario
User = get_user_model()
logger = logging.getLogger(__name__)

### FUNCIONES AUXILIARES ###

# Decorador para verificar si el usuario ha iniciado sesión.
# Si no lo ha hecho, lo redirige a la página de inicio de sesión con un mensaje.
def login_required_with_message(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Por favor, inicie sesión para acceder a esta página.")
            return redirect('login')  # Redirige al login si el usuario no está autenticado
        return view_func(request, *args, **kwargs)
    return _wrapped_view

### VISTAS GENERALES ###
# Página de inicio
def index(request):
    numero = 0  # Variable de prueba
    return render(request, "index.html", {'numero': numero})

# Página principal (home)
def Home(request):
    numero = 0  # Variable de prueba
    return render(request, 'index.html', {'numero': numero})

# Página de inicio de sesión
def Login(request):
    numero = 0  # Variable de prueba
    return render(request, 'login.html', {'numero': numero})

# Registro de usuarios
def Register(request):
    numero = 0
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)  # Formulario personalizado de registro
        if form.is_valid():
            user = form.save()  # Guarda el usuario
            login(request, user)  # Autentica automáticamente al usuario después de registrarse
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})

### VISTAS RESTRINGIDAS ###
# Menú principal (requiere inicio de sesión)
@login_required_with_message
def main_Menu(request):
    numero = 1  # Variable de prueba
    return render(request, 'main_menu.html', {'numero': numero})

# Página de estatus (requiere inicio de sesión)
@login_required_with_message
def Estatus(request):
    numero = 1  # Variable de prueba
    return render(request, 'estatus.html', {'numero': numero})

@login_required_with_message
def Restore_Password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()  # Guarda la nueva contraseña
            update_session_auth_hash(request, user)  # Mantiene al usuario autenticado
            messages.success(request, "Contraseña Restablecida exitosamente")
            return redirect("home")
        else:
            messages.error(request, 'Por favor corrige los errores indicados.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'restore_password.html', {'form': form})



### FLUJO DE VERIFICACIÓN Y RESTABLECIMIENTO DE CONTRASEÑA ###

# Verificar usuario mediante email y número de control
def Forgot_Password(request):
    if request.method == "POST":
        form = VerifyUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")  # Número de control
            email = form.cleaned_data.get("email")  # Correo electrónico
            # Guarda temporalmente el usuario en la sesión
            request.session['verified_user'] = {
                'username': username,
                'email': email,
            }
            messages.success(request, "Usuario verificado correctamente. Proceda a restablecer su contraseña.")
            return redirect("update_password")
    else:
        form = VerifyUserForm()
    return render(request, "forgot_password.html", {"form": form})

# Página de restablecimiento de contraseña para usuarios no autenticados
def Update_Password(request):
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            new_password = form.cleaned_data.get('password')

            verified_user = request.session.get('verified_user')
            if verified_user != {'username': username, 'email': email}:
                messages.error(request, "Primero verifica tu usuario y correo para restablecer la contraseña.")
                return redirect("forgot_password")

            try:
                # Validar que el usuario existe
                user = User.objects.get(username=username, email=email)
                # Actualizar la contraseña
                user.set_password(new_password)
                user.save()
                request.session.pop('verified_user', None)
                messages.success(request, "Tu contraseña se ha restablecido correctamente. Por favor, inicia sesión.")
                return redirect("login")  # Reemplaza 'login' con el nombre de tu URL de inicio de sesión
            except User.DoesNotExist:
                messages.error(request, "El usuario no existe o la información es incorrecta.")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = ResetPasswordForm()

    # Para solicitudes GET o si el formulario es inválido
    return render(request, "update_password.html", {"form": form})



### VISTA PARA ENVÍO DE CORREO ###
@login_required_with_message
def enviar_correo(request):
    asunto = 'Restablecimiento de contraseña'
    mensaje = 'Codigo: '  # Cambiar por contenido dinámico si es necesario
    destinatarios = [request.user.email]
    try:
        send_mail(asunto, mensaje, None, destinatarios)
        return HttpResponse('Correo enviado exitosamente.')
    except Exception:
        logger.exception("No fue posible enviar el correo de restablecimiento")
        return HttpResponse('No fue posible enviar el correo.', status=500)

### VISTA PERSONALIZADA DE INICIO DE SESIÓN ###
class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('main_menu')  # Redirige al menú principal tras iniciar sesión
