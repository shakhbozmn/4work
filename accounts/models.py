from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    ROLE_CHOICES = (
        ("client", "Client"),
        ("freelancer", "Freelancer"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("accounts:profile_detail", kwargs={"username": self.username})


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    # Freelancer-only
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True, related_name="profiles")
    # Client-only
    company_name = models.CharField(max_length=200, blank=True, default="")
    # Shared
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_absolute_url(self):
        return reverse("accounts:profile_detail", kwargs={"username": self.user.username})
