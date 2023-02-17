from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import Document, Element


class PermissionClass:

    @classmethod
    def has_permission(cls, info):
        user = info.context.user
        if not user:
            raise PermissionDenied({'error': 'you are not authenticated'})
        if user.is_invited:
            return user
        subs_end = user.subscription.end_datetime
        if subs_end.astimezone(tz=timezone.utc) < timezone.now():
            raise PermissionDenied({'error': 'you subscription is over'})
        return user

    @classmethod
    def has_query_object_permission(cls, info, doc_id):
        doc = Document.objects.get(pk=doc_id)
        user = info.context.user
        if not user.has_object_perm(doc, ['read', 'edit', 'own']) and not user.is_invited:
            raise PermissionDenied(
                {'error': 'You don`t have access to this object'})

    @classmethod
    def has_mutate_object_permission(cls, info, doc_id):
        doc = Document.objects.filter(pk=doc_id).first()
        user = info.context.user
        if not user.has_object_perm(doc, ['edit', 'own']):
            raise PermissionDenied(
                {'error': 'You don`t have access to this object'})
