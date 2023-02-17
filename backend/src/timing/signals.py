from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Timing
from .schema import TimingOnNewChatMessage


@receiver(post_save, sender=Timing)
def timing_updated(sender, instance, **kwargs):
    if instance.doc_uuid:
        TimingOnNewChatMessage.message_about_changing(chatroom=str(instance.doc_uuid), instance=instance)
