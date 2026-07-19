from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Skill

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    def test_user_creation(self):
        """Test that a user can be created successfully"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("testpass123"))

    def test_user_str_method(self):
        """Test the __str__ method of User model"""
        self.assertEqual(str(self.user), "testuser")

    def test_user_role_choices(self):
        """Test that role choices are valid"""
        user_client = User.objects.create_user(
            username="clientuser",
            email="client@example.com",
            password="testpass123",
            role="client",
        )
        self.assertEqual(user_client.role, "client")

    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.user.get_absolute_url()
        self.assertEqual(url, f"/accounts/profile/{self.user.username}/")


class ProfileModelTest(TestCase):
    """Test cases for Profile model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.skill = Skill.objects.create(name="Python")

    def test_profile_auto_creation(self):
        """Test that profile is automatically created with user"""
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertEqual(self.user.profile.user, self.user)

    def test_profile_str_method(self):
        """Test the __str__ method of Profile model"""
        self.assertEqual(str(self.user.profile), f"{self.user.username}'s Profile")

    def test_profile_skills_relationship(self):
        """Test that profile can have multiple skills"""
        self.user.profile.skills.add(self.skill)
        self.assertEqual(self.user.profile.skills.count(), 1)
        self.assertIn(self.skill, self.user.profile.skills.all())

    def test_profile_hourly_rate(self):
        """Test hourly rate field"""
        self.user.profile.hourly_rate = 50.00
        self.user.profile.save()
        self.assertEqual(self.user.profile.hourly_rate, 50.00)

    def test_profile_bio(self):
        """Test bio field"""
        bio = "Experienced developer"
        self.user.profile.bio = bio
        self.user.profile.save()
        self.assertEqual(self.user.profile.bio, bio)


class SkillModelTest(TestCase):
    """Test cases for Skill model"""

    def setUp(self):
        self.skill = Skill.objects.create(name="Python")

    def test_skill_creation(self):
        """Test that a skill can be created successfully"""
        self.assertEqual(self.skill.name, "Python")

    def test_skill_str_method(self):
        """Test the __str__ method of Skill model"""
        self.assertEqual(str(self.skill), "Python")
