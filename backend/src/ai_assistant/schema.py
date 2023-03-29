import datetime
import uuid
import graphene
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required
from graphene_django.types import ObjectType, DjangoObjectType
from graphene_file_upload.scalars import Upload
from rest_framework.generics import get_object_or_404

from ai_assistant.models import AiAssistant
from graphql_utils.utils_graphql import PermissionClassFolder


class AiAssistantType(DjangoObjectType):
    perm = graphene.String()
    perms = graphene.List(graphene.String)

    class Meta:
        model = AiAssistant

    @staticmethod
    def resolve_perm(self, info):
        user = info.context.user
        folder = self.folder
        perms = user.get_object_perm_as_str_list(folder)
        return perms[0] if len(perms) == 1 else perms

    @staticmethod
    def resolve_perms(self, info):
        return self.perms


class Query(ObjectType):
    all_ai_assistants = graphene.List(AiAssistantType)
    ai_assistant_by_id = graphene.Field(AiAssistantType, ai_assist_id=graphene.ID())

    @login_required
    def resolve_all_ai_assistants(self, info):
        """
        Resolve all Ai_Assistants
        """
        PermissionClassFolder.has_permission(info)
        ret = AiAssistant.objects.filter(
            owner=info.context.user,
            deleted_id__isnull=True,
        ).all()
        return ret

    @login_required
    def resolve_ai_assistant_by_id(self, info, ai_assist_id=None):
        """
        Resolve Ai_Assistant by ai_assist_id
        """
        PermissionClassFolder.has_permission(info)
        ret = get_object_or_404(AiAssistant, id=ai_assist_id)
        PermissionClassFolder.has_query_object_permission(info, ret)

        return ret


class Mutation(ObjectType):
    pass
