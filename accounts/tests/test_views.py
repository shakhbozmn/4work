from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class LoginViewTest(TestCase):
    """Test cases for login view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth/login.html")

    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "testpass123"},
        )
        self.assertRedirects(response, reverse("accounts:dashboard"))

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)


class RegisterViewTest(TestCase):
    """Test cases for register view"""

    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        """Test that register page loads successfully"""
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth/register.html")

    def test_register_with_valid_data(self):
        """Test registration with valid data"""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "testpass123",
                "password2": "testpass123",
                "role": "freelancer",
            },
        )
        self.assertRedirects(response, reverse("accounts:dashboard"))
        self.assertTrue(User.objects.filter(username="newuser").exists())


class LogoutViewTest(TestCase):
    """Test cases for logout view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.client.login(username="testuser", password="testpass123")

    def test_logout(self):
        """Test that logout works correctly"""
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))


class ProfileDetailViewTest(TestCase):
    """Test cases for profile detail view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="freelancer",
        )
        self.client.login(username="testuser", password="testpass123")

    def test_profile_detail_page_loads(self):
        """Test that profile detail page loads successfully"""
        response = self.client.get(reverse("accounts:profile_detail", args=["testuser"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile_detail.html")

    def test_profile_detail_displays_user_info(self):
        """Test that profile detail displays user information"""
        self.user.profile.bio = "Test bio"
        self.user.profile.hourly_rate = 50.00
        self.user.profile.save()

        response = self.client.get(reverse("accounts:profile_detail", args=["testuser"]))
        self.assertContains(response, "testuser")
        self.assertContains(response, "Test bio")
        self.assertContains(response, "50.00")


class ProfileUpdateViewTest(TestCase):
    """Test cases for profile update view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="freelancer",
        )
        self.client.login(username="testuser", password="testpass123")

    def test_profile_update_page_loads(self):
        """Test that profile update page loads successfully"""
        response = self.client.get(reverse("accounts:profile_update"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile_update.html")

    def test_profile_update_with_valid_data(self):
        """Test profile update with valid data"""
        response = self.client.post(
            reverse("accounts:profile_update"),
            {"bio": "Updated bio", "hourly_rate": "75.00", "skills": []},
        )
        self.assertRedirects(response, reverse("accounts:profile_detail", args=["testuser"]))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, "Updated bio")
        self.assertEqual(self.user.profile.hourly_rate, 75.00)

    def test_profile_update_requires_login(self):
        """Test that profile update requires login"""
        self.client.logout()
        response = self.client.get(reverse("accounts:profile_update"))
        self.assertEqual(response.status_code, 302)
