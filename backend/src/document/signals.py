from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Document
from .schema import OnNewChatMessage


@receiver(post_save, sender=Document)
def document_updated(sender, instance, **kwargs):
    if instance.doc_uuid:
        OnNewChatMessage.message_about_changing(chatroom=str(instance.doc_uuid), instance=instance)
