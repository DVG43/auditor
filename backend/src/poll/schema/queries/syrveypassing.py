import graphene
from graphene_django.types import ObjectType
from graphql_jwt.decorators import login_required

from graphql_utils.utils_graphql import PermissionClass
from poll.schema import types
from poll.models import surveypassing
from rest_framework.generics import get_object_or_404


class QuerySurveyPassing(ObjectType):
    all_sp = graphene.List(types.SurveyPassingType)
    surverpassing_by_id = graphene.Field(types.SurveyPassingType, sp_id=graphene.Int())

    @login_required
    def resolve_all_sp(self, info):
        PermissionClass.has_permission(info)
        ret = surveypassing.SurveyPassing.objects.all().select_related("user").prefetch_related(
            "useranswerquestion_set",
            "poll__manyfromlistquestion_set__items",
            "poll__freeanswer_set__tags",
            "poll__freeanswer_set__attached_type",
            "poll__freeanswer_set__items__tags",
            "poll__yesnoquestion_set__items",
            "poll__yesnoquestion_set__yes_no_answers",
            "poll__yesnoquestion_set__attached_type",
            "poll__mediaquestion_set__attached_type",
            "poll__mediaquestion_set__items",
        ).filter(
            user=info.context.user,
        ).all()
        return ret

    @login_required
    def surverpassing_by_id(self, info, id=None):
        PermissionClass.has_permission(info)

        ret = get_object_or_404(surveypassing.SurveyPassing, id=id)
        prj_id = ret.host_project.id
        PermissionClass.has_query_object_permission(info, prj_id)

        return ret
