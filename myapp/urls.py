from django.urls import path
from . import views
from .views import CustomLoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Ruta principal de inicio (vista de inicio)
    path('', views.Home),  # Carga la vista "Home" sin un nombre asignado.

    # Página de índice con el nombre 'home'
    path('index/', views.index, name='home'),  # Vista inicial del proyecto.
    
    # Ruta alternativa para la vista de inicio
    path('inicio/', views.Home, name='inicio'),  # Ruta accesible mediante '/inicio'.

    # Página de inicio de sesión con una vista personalizada
    path('login/', CustomLoginView.as_view(), name='login'),  # Vista basada en clase para iniciar sesión.

    # Ruta para verificar información de seguridad de la contraseña
    path('forgot_password/', views.Forgot_Password, name='forgot_password'),

    # Página para registrar nuevos usuarios
    path('register/', views.Register, name='register'),

    # Menú principal
    path('main_menu/', views.main_Menu, name='main_menu'),

    # Página para el estatus de los usuarios
    path('estatus/', views.Estatus, name='estatus'),

    # Restablecimiento de contraseña
    path('restore_Password/', views.Restore_Password, name='restore_Password'),

    # Restablecimiento de contraseña con validación adicional
    path('update_password/', views.Update_Password, name='update_password'),

    # Envío de correos electrónicos
    path('enviar-correo/', views.enviar_correo, name='enviar_correo'),

    # Cierre de sesión
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]
