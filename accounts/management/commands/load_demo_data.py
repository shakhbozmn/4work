"""Load the demo data set used by the local Docker stack.

Running this command more than once is safe: it is idempotent across
categories, skills, and demo users. Project deadlines are recomputed
relative to the current date on each run so the demo never goes stale.
"""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

User = get_user_model()


DEMO_PASSWORD = "password123"
ADMIN_USERNAME = "adminus"
ADMIN_PASSWORD = "admin123us"

DEMO_USERS = [
    {
        "username": "john_client",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "role": "client",
    },
    {
        "username": "jane_freelancer",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "role": "freelancer",
    },
    {
        "username": "bob_freelancer",
        "first_name": "Bob",
        "last_name": "Johnson",
        "email": "bob@example.com",
        "role": "freelancer",
    },
]

DEMO_PROJECT_DEADLINE_OFFSETS = {
    1: timedelta(days=30),
    2: timedelta(days=45),
    3: timedelta(days=60),
}


class Command(BaseCommand):
    help = (
        "Load demo data including categories, skills, and sample projects. "
        "Idempotent: re-running resets passwords and refreshes project deadlines."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Allow seeding in production settings (still requires DEBUG=False path).",
        )

    def handle(self, *args, **options):
        if settings.DEBUG is False and not options["force"]:
            raise CommandError(
                "Refusing to seed demo data while DEBUG=False. " "Run with --force only if you really mean it."
            )

        self.stdout.write(self.style.SUCCESS("Loading demo data..."))

        try:
            with transaction.atomic():
                self._loaddata("categories", "categories")
                self._loaddata("skills", "skills")
                self._loaddata("demo_data", "demo records")

                self._refresh_project_deadlines()
                self._set_demo_passwords()
                self._seed_admin()
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"\nError loading demo data: {exc}"))
            raise

        self._print_summary()

    def _loaddata(self, fixture_path: str, label: str) -> None:
        self.stdout.write(f"Loading {label}...")
        call_command("loaddata", fixture_path)
        self.stdout.write(self.style.SUCCESS(f"{label.capitalize()} loaded successfully"))

    def _refresh_project_deadlines(self) -> None:
        from marketplace.models import Project

        seed_date = timezone.localdate()
        for project_id, offset in DEMO_PROJECT_DEADLINE_OFFSETS.items():
            Project.objects.filter(pk=project_id).update(deadline=seed_date + offset)
        self.stdout.write(self.style.SUCCESS("Project deadlines refreshed"))

    def _set_demo_passwords(self) -> None:
        for spec in DEMO_USERS:
            user, _ = User.objects.update_or_create(
                username=spec["username"],
                defaults={
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                    "email": spec["email"],
                    "role": spec["role"],
                    "is_active": True,
                },
            )
            user.set_password(DEMO_PASSWORD)
            user.save(update_fields=["password"])
        self.stdout.write(self.style.SUCCESS("Demo user passwords set"))

    def _seed_admin(self) -> None:
        from .models import Profile

        admin, _ = User.objects.update_or_create(
            username=ADMIN_USERNAME,
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "email": "admin@example.com",
                "role": "client",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        admin.set_password(ADMIN_PASSWORD)
        admin.save(update_fields=["password"])
        Profile.objects.get_or_create(user=admin)
        self.stdout.write(self.style.SUCCESS(f"Admin user '{ADMIN_USERNAME}' seeded"))

    def _print_summary(self) -> None:
        self.stdout.write(self.style.SUCCESS("\nAll demo data loaded successfully!"))
        self.stdout.write("\nDemo accounts:")
        self.stdout.write("  Client:    john_client / password123")
        self.stdout.write("  Freelancer: jane_freelancer / password123")
        self.stdout.write("  Freelancer: bob_freelancer / password123")
        self.stdout.write(f"  Admin:     {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
