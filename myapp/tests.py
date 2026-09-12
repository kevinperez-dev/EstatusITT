from django.test import TestCase
from .models import CustomUser
from django.urls import reverse
from .forms import CustomUserCreationForm
from myapp.models import CustomUser
# Create your tests here.


class CustomUserModelTest(TestCase):
    def setUp(self):
        # Configuración inicial para los casos de prueba
        self.user = CustomUser.objects.create(
            username="testuser",
            email="testuser@example.com",
            carrera="Sistemas Computacionales",
            nivel_educativo="LIC"
        )
    
    def test_user_creation(self):
        # Verificar si el usuario fue creado correctamente
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")
    
    def test_user_carrera(self):
        # Verificar que el campo carrera sea correcto
        self.assertEqual(self.user.carrera, "Sistemas Computacionales")


class HomePageTest(TestCase):
    def test_home_page_status_code(self):
        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.status_code, 200)

class CustomUserCreationFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'strongpassword',
            'password2': 'strongpassword',
            'carrera': 'Sistemas Computacionales',
            'nivel_educativo': 'LIC'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

class RegisterViewTest(TestCase):
    def test_register_user_successfully(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'carrera': 'Sistemas Computacionales',
            'nivel_educativo': 'LIC',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        })
        self.assertEqual(response.status_code, 302)  # Redirección exitosa
        self.assertTrue(CustomUser.objects.filter(username='testuser').exists())


class PasswordResetFlowTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='control123',
            email='control123@example.com',
            password='OriginalPassword123!',
            carrera='Sistemas Computacionales',
            nivel_educativo='LIC',
        )

    def test_password_reset_requires_prior_verification(self):
        response = self.client.post(reverse('update_password'), {
            'username': self.user.username,
            'email': self.user.email,
            'password': 'NewPassword123!',
        })

        self.assertRedirects(response, reverse('forgot_password'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OriginalPassword123!'))

    def test_verified_user_can_reset_password(self):
        verification = self.client.post(reverse('forgot_password'), {
            'username': self.user.username,
            'email': self.user.email,
        })
        self.assertRedirects(verification, reverse('update_password'))

        response = self.client.post(reverse('update_password'), {
            'username': self.user.username,
            'email': self.user.email,
            'password': 'NewPassword123!',
        })

        self.assertRedirects(response, reverse('login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))
