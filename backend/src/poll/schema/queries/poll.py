import graphene
from graphene_django.types import ObjectType
from graphql_jwt.decorators import login_required
from rest_framework.generics import get_object_or_404

from graphql_utils.utils_graphql import PermissionClass
from poll.schema import types
from poll.models import (
    poll as poll_models,
)


class QueryPoll(ObjectType):
    all_polls = graphene.List(types.PollType)
    all_poll_tags = graphene.List(types.PollTagsType, poll_id=graphene.Int())
    poll_by_id = graphene.Field(types.PollType, poll_id=graphene.Int())
    poll_setting_by_id = graphene.Field(types.PollSettingsType, poll_id=graphene.Int())
    poll_tag_by_id = graphene.Field(types.PollTagsType, tag_id=graphene.Int())

    @login_required
    def resolve_all_polls(self, info):
        PermissionClass.has_permission(info)
        # PermissionClass.has_query_object_permission(info, prj_id)
        ret = poll_models.Poll.objects.filter(
            owner=info.context.user,
            deleted_id__isnull=True,
        ).all()
        return ret

    @login_required
    def resolve_all_poll_tags(self, info, poll_id=None):
        PermissionClass.has_permission(info)
        # PermissionClass.has_query_object_permission(info, prj_id)
        ret = poll_models.PollTags.objects.filter(
            poll=poll_id).all()
        return ret

    @login_required
    def resolve_poll_by_id(self, info, poll_id=None):
        PermissionClass.has_permission(info)

        ret = get_object_or_404(poll_models.Poll, id=poll_id)
        # prj_id = ret.host_project.id
        # PermissionClass.has_query_object_permission(info, prj_id)

        return ret

    @login_required
    def resolve_poll_setting_by_id(self, info, poll_id=None):
        PermissionClass.has_permission(info)

        ret = poll_models.PollSettings.objects.get(id=poll_id)
        prj_id = ret.poll.host_project.id
        PermissionClass.has_query_object_permission(info, prj_id)

        return ret

    @login_required
    def resolve_poll_tag_by_id(self, info, tag_id=None):
        PermissionClass.has_permission(info)

        ret = poll_models.PollTags.objects.get(tag_id=tag_id)
        polls = ret.poll_set.all()
        for poll in polls:
            prj_id = poll.host_project.id
            PermissionClass.has_query_object_permission(info, prj_id)

        return ret
