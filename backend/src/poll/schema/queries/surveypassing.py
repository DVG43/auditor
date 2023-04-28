import graphene
from graphene_django.types import ObjectType
from graphql_jwt.decorators import login_required

from graphql_utils.permissions import PermissionClass
from poll.models.poll import Poll
from poll.models.surveypassing import SurveyPassing
from poll.schema import types
from rest_framework.generics import get_object_or_404


class QuerySurveyPassing(ObjectType):
    """
    Query for getting SurveyPassing
    """
    all_survey = graphene.List(types.SurveyPassingType)
    survey_passing_by_poll_id = graphene.List(types.SurveyPassingType, id=graphene.Int())

    @login_required
    def resolve_all_survey(self, info):
        """
        Resolve all SurveyPassing
        """
        PermissionClass.has_permission(info)
        ret = SurveyPassing.objects.filter(poll__owner=info.context.user)
        return ret

    @login_required
    def resolve_survey_passing_by_poll_id(self, info, id=None):
        """
        Resolve SurveyPassing by id
        """
        PermissionClass.has_permission(info)
        poll = get_object_or_404(Poll, id=id)
        PermissionClass.has_query_object_permission(info, poll)

        ret = SurveyPassing.objects.filter(poll=poll)
        return ret
