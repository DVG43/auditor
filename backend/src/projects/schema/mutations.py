import graphene
from django.utils import timezone
from graphene_django.rest_framework.mutation import SerializerMutation
from graphene_django.types import ErrorType

from projects.models import Link, Text
from projects.serializers import LinkSerializer, TextSerializer


class CreateUpdateLink(SerializerMutation):
    class Meta:
        serializer_class = LinkSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'
        model_class = Link


class CreateUpdateText(SerializerMutation):
    class Meta:
        serializer_class = TextSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'
        model_class = Text


class LinkMutation(graphene.ObjectType):
    crt_upd_link = CreateUpdateLink.Field()


class TextMutation(graphene.ObjectType):
    crt_upd_text = CreateUpdateText.Field()


class Mutation(LinkMutation, TextMutation, graphene.ObjectType):
    pass
