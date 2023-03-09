import graphene
from graphene_django.types import ObjectType
from graphql_jwt.decorators import login_required
from rest_framework.generics import get_object_or_404

from graphql_utils.utils_graphql import PermissionClass
from projects.schema import types
from projects.models import Link, Text


class QueryLink(graphene.ObjectType):
    all_links = graphene.List(types.LinkType)
    link_by_id = graphene.Field(types.LinkType, link_id=graphene.Int())

    @login_required
    def resolve_all_links(self, info):
        PermissionClass.has_permission(info)
        ret = Link.objects.filter(
            owner=info.context.user,
            deleted_id__isnull=True,
        ).all()
        return ret

    @login_required
    def resolve_link_by_id(self, info, link_id=None):
        PermissionClass.has_permission(info)

        ret = get_object_or_404(Link, id=link_id)

        return ret


class QueryText(graphene.ObjectType):
    all_texts = graphene.List(types.TextType)
    text_by_id = graphene.Field(types.TextType, text_id=graphene.Int())

    @login_required
    def resolve_all_texts(self, info):
        PermissionClass.has_permission(info)
        ret = Text.objects.filter(
            owner=info.context.user,
            deleted_id__isnull=True,
        ).all()
        return ret

    @login_required
    def resolve_text_by_id(self, info, text_id=None):
        PermissionClass.has_permission(info)

        ret = get_object_or_404(Text, id=text_id)

        return ret


class Query(QueryLink, QueryText, graphene.ObjectType):
    pass
