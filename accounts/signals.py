from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a Profile instance when a new User is created."""
    # Avoid touching the DB while loading fixtures (raw=True), which already
    # creates the related Profile rows explicitly.
    if not created or kwargs.get("raw"):
        return
    Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Persist the related Profile whenever a User is saved."""
    if kwargs.get("raw"):
        return
    if hasattr(instance, "profile"):
        instance.profile.save()
