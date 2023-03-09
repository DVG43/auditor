import graphene
from graphene_django.types import DjangoObjectType

from projects.models import Link, Text


class LinkType(DjangoObjectType):
    class Meta:
        model = Link


class TextType(DjangoObjectType):
    class Meta:
        model = Text
