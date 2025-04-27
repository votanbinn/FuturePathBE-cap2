# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models

@receiver(post_save, sender=models.BannedUserHistory)
def ban_user(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.status = True
        user.save()