"""Tests for the `load_demo_data` management command."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from marketplace.models import Application, Project

User = get_user_model()


class LoadDemoDataCommandTest(TestCase):
    """Verify the demo seeder is correct and idempotent."""

    def _run(self):
        call_command("load_demo_data")

    def test_first_load_seeds_expected_counts(self):
        self._run()

        self.assertEqual(
            User.objects.filter(username__in=["john_client", "jane_freelancer", "bob_freelancer"]).count(),
            3,
        )
        self.assertTrue(User.objects.filter(username="adminus", is_superuser=True).exists())
        self.assertEqual(Project.objects.count(), 3)
        self.assertEqual(Application.objects.count(), 3)

    def test_project_deadlines_are_in_the_future(self):
        self._run()

        today = timezone.localdate()
        for project in Project.objects.all():
            self.assertIsNotNone(project.deadline)
            self.assertGreaterEqual(project.deadline, today)

    def test_deadline_offsets_match_spec(self):
        self._run()

        today = timezone.localdate()
        expected = {
            1: today + timedelta(days=30),
            2: today + timedelta(days=45),
            3: today + timedelta(days=60),
        }
        for pk, deadline in expected.items():
            self.assertEqual(Project.objects.get(pk=pk).deadline, deadline)

    def test_second_load_is_idempotent(self):
        self._run()
        first_users = User.objects.count()
        first_projects = Project.objects.count()
        first_applications = Application.objects.count()

        self._run()

        self.assertEqual(User.objects.count(), first_users)
        self.assertEqual(Project.objects.count(), first_projects)
        self.assertEqual(Application.objects.count(), first_applications)

    def test_demo_passwords_authenticate(self):
        self._run()

        from django.contrib.auth import authenticate

        for username in ["john_client", "jane_freelancer", "bob_freelancer"]:
            self.assertIsNotNone(authenticate(username=username, password="password123"))
        self.assertIsNotNone(authenticate(username="adminus", password="admin123us"))

    def test_refuses_to_run_when_debug_is_false(self):
        from django.core.management.base import CommandError

        with override_settings(DEBUG=False):
            with self.assertRaises(CommandError):
                self._run()

    def test_force_flag_allows_run_when_debug_is_false(self):
        with override_settings(DEBUG=False):
            self._run()
            self.assertTrue(User.objects.filter(username="adminus").exists())
