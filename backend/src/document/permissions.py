from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import Document, Element
from graphql_utils.utils_graphql import \
    PermissionClass


class PermissionClass(PermissionClass):

    @classmethod
    def has_query_object_permission(cls, info, doc_id):
        doc = Document.objects.get(pk=doc_id)
        user = info.context.user
        if not user.has_object_perm(doc, ['read', 'edit', 'own']) and not user.is_invited:
            folder = doc.folder
            while folder:
                if user.has_object_perm(folder, ['read', 'edit', 'own']):
                    break
                folder = folder.parent_folder
            if not folder:
                raise PermissionDenied(
                    {'error': f'You don`t have access to this object: {doc}'})

    @classmethod
    def has_mutate_object_permission(cls, info, doc_id):
        doc = Document.objects.filter(pk=doc_id).first()
        user = info.context.user
        if not user.has_object_perm(doc, ['edit', 'own']) and not user.is_invited:
            folder = doc.folder
            while folder:
                if user.has_object_perm(folder, ['edit', 'own']):
                    break
                folder = folder.parent_folder
            if not folder:
                raise PermissionDenied(
                    {'error': f'You don`t have access to this object: {doc}'})
