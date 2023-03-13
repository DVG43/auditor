import uuid

import graphene
from django.utils import timezone
from graphene_django.rest_framework.mutation import SerializerMutation
from graphene_django.types import ErrorType
from graphql_jwt.decorators import login_required

from projects.models import Link, Text
from projects.serializers import LinkSerializer, TextSerializer

from graphql_utils.permissions import PermissionClass


class CreateUpdateLink(SerializerMutation):
    class Meta:
        serializer_class = LinkSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'
        model_class = Link


class DeleteLink(graphene.Mutation):

    class Arguments:
        link_id = graphene.ID()

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, root, link_id):
        link = Link.objects.filter(id=link_id).first()
        PermissionClass.has_permission(root)
        if link:
            link.deleted_id = uuid.uuid4()
            link.deleted_since = timezone.now()
            link.save()
            return DeleteLink(ok=True)
        else:
            return DeleteLink(ok=False)


class CreateUpdateText(SerializerMutation):
    class Meta:
        serializer_class = TextSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'
        model_class = Text


class DeleteText(graphene.Mutation):

    class Arguments:
        text_id = graphene.ID()

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, root, text_id):
        text = Text.objects.filter(id=text_id).first()
        PermissionClass.has_permission(root)
        if text:
            text.deleted_id = uuid.uuid4()
            text.deleted_since = timezone.now()
            text.save()
            return DeleteText(ok=True)
        else:
            return DeleteText(ok=False)


class LinkMutation(graphene.ObjectType):
    crt_upd_link = CreateUpdateLink.Field()
    delete_link = DeleteLink.Field()


class TextMutation(graphene.ObjectType):
    crt_upd_text = CreateUpdateText.Field()
    delete_text = DeleteText.Field()


class Mutation(LinkMutation, TextMutation, graphene.ObjectType):
    pass
