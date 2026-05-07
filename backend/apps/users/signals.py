from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    User yaratilganda unga Profile ob'ektini avtomatik qo'shish.
    Bu tahrirlashda Profile.DoesNotExist xatosining oldini oladi.
    """
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """User saqlanganda uning profilini ham saqlash."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
