from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("marketplace:category_detail", kwargs={"pk": self.pk})


class Project(models.Model):
    STATUS_CHOICES = (
        ("open", "Open"),
        ("assigned", "Assigned"),
        ("completed", "Completed"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="projects")
    assigned_freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_projects",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    skills = models.ManyToManyField("accounts.Skill", blank=True, related_name="projects")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("marketplace:project_detail", kwargs={"pk": self.pk})

    @property
    def accepts_applications(self) -> bool:
        """A project is open for new applications when it is still open and
        its deadline (if set) has not passed."""
        if self.status != "open":
            return False
        if self.deadline is None:
            return True
        return self.deadline >= timezone.localdate()


class Application(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("rejected", "Rejected"),
        ("accepted", "Accepted"),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="applications")
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")

    cover_letter = models.TextField()
    proposed_timeline = models.PositiveIntegerField(help_text="Timeline in days")
    proposed_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("project", "freelancer")
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    def __str__(self):
        return f"{self.freelancer.username} - {self.project.title}"

    def get_absolute_url(self):
        return reverse("marketplace:project_detail", kwargs={"pk": self.project_id})

