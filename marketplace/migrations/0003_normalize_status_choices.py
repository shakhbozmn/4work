# Normalize the dropped intermediate status values and shrink the choice lists.

from django.db import migrations, models


def normalize_statuses(apps, schema_editor):
    Project = apps.get_model("marketplace", "Project")
    Application = apps.get_model("marketplace", "Application")
    Project.objects.filter(status="reviewing").update(status="open")
    Application.objects.filter(status="shortlisted").update(status="pending")


def reverse_normalize_statuses(apps, schema_editor):
    # Reverse data migration cannot restore the distinction that was collapsed.
    # Leave rows at their normalized values; only the choices are reverted.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0002_project_skills"),
    ]

    operations = [
        migrations.RunPython(normalize_statuses, reverse_normalize_statuses),
        migrations.AlterField(
            model_name="project",
            name="status",
            field=models.CharField(
                choices=[("open", "Open"), ("assigned", "Assigned"), ("completed", "Completed")],
                default="open",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="application",
            name="status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("rejected", "Rejected"), ("accepted", "Accepted")],
                default="pending",
                max_length=20,
            ),
        ),
    ]
