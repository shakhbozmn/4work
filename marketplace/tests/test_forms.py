"""Tests for marketplace forms and model properties."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from marketplace.forms import ApplicationForm, ProjectForm
from marketplace.models import Application, Category, Project, Skill

User = get_user_model()


class ProjectModelPropertyTest(TestCase):
    def setUp(self):
        self.client = User.objects.create_user(
            username="client", email="c@example.com", password="pw", role="client"
        )
        self.category = Category.objects.create(name="Web")

    def _make(self, status="open", deadline=None):
        return Project.objects.create(
            title="Project",
            description="Body",
            budget="1000.00",
            deadline=deadline,
            client=self.client,
            category=self.category,
            status=status,
        )

    def test_open_no_deadline_accepts_applications(self):
        self.assertTrue(self._make(status="open").accepts_applications)

    def test_open_future_deadline_accepts_applications(self):
        future = timezone.localdate() + timedelta(days=5)
        self.assertTrue(self._make(status="open", deadline=future).accepts_applications)

    def test_open_past_deadline_rejects_applications(self):
        past = timezone.localdate() - timedelta(days=1)
        self.assertFalse(self._make(status="open", deadline=past).accepts_applications)

    def test_assigned_rejects_applications(self):
        self.assertFalse(self._make(status="assigned").accepts_applications)

    def test_completed_rejects_applications(self):
        self.assertFalse(self._make(status="completed").accepts_applications)


class ProjectFormTest(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client", email="c@example.com", password="pw", role="client"
        )
        self.category = Category.objects.create(name="Web")
        self.python = Skill.objects.create(name="Python")
        self.django = Skill.objects.create(name="Django")

    def test_valid_form_persists_skills(self):
        form = ProjectForm(
            data={
                "title": "Build app",
                "description": "Body",
                "budget": "1000.00",
                "deadline": (timezone.localdate() + timedelta(days=10)).isoformat(),
                "category": str(self.category.pk),
                "skills": [str(self.python.pk), str(self.django.pk)],
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        project = form.save(commit=False)
        project.client = self.client_user
        project.save()
        form.save_m2m()
        project.refresh_from_db()
        self.assertEqual(set(project.skills.all()), {self.python, self.django})

    def test_past_deadline_rejected(self):
        form = ProjectForm(
            data={
                "title": "Old",
                "description": "Body",
                "budget": "100.00",
                "deadline": (timezone.localdate() - timedelta(days=1)).isoformat(),
                "category": str(self.category.pk),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("deadline", form.errors)


class ApplicationFormTest(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client", email="c@example.com", password="pw", role="client"
        )
        self.freelancer = User.objects.create_user(
            username="fler", email="f@example.com", password="pw", role="freelancer"
        )
        self.project = Project.objects.create(
            title="P",
            description="B",
            budget="100.00",
            client=self.client_user,
            status="open",
        )

    def test_persists_proposed_budget(self):
        form = ApplicationForm(
            data={
                "cover_letter": "Hi",
                "proposed_timeline": "14",
                "proposed_budget": "950.00",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        application = form.save(commit=False)
        application.project = self.project
        application.freelancer = self.freelancer
        application.save()
        stored = Application.objects.get(pk=application.pk)
        self.assertEqual(stored.proposed_budget, application.proposed_budget)
