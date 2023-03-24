import graphene
from graphene_django.types import ObjectType
from graphql_jwt.decorators import login_required

from poll.permissions import PermissionPollClass
from poll.schema import types
from poll.models.answer import UserAnswerQuestion
from poll.models.poll import Poll
from poll.models.surveypassing import SurveyPassing


class QueryUserAnswers(ObjectType):
    """
    Query for getting answers
    """
    all_user_answers = graphene.List(types.UserAnswerQuestionType)
    user_answers_by_poll_id = graphene.List(types.UserAnswerQuestionType,
                                            poll_id=graphene.Int())
    user_answers_by_survey_id = graphene.List(types.UserAnswerQuestionType,
                                              survey_id=graphene.Int())

    @login_required
    def resolve_all_user_answers(self, info):
        """
        Resolve all UserAnswers
        """
        PermissionPollClass.has_permission(info)
        ret = UserAnswerQuestion.objects\
            .select_related("survey", "survey__poll")\
            .all()
        return ret

    @login_required
    def resolve_user_answers_by_poll_id(self, info, poll_id=None):
        """
        Resolve UserAnswers by id
        """
        PermissionPollClass.has_permission(info)

        ret = UserAnswerQuestion.objects\
            .select_related("survey", "survey__poll")\
            .filter(poll_id=poll_id)\
            .all()
        poll = Poll.objects.get(id=poll_id)
        PermissionPollClass.has_query_object_permission(info, poll)

        return ret

    @login_required
    def resolve_user_answers_by_survey_id(self, info, survey_id=None):
        """
        Resolve UserAnswers by id
        """
        PermissionPollClass.has_permission(info)

        ret = UserAnswerQuestion.objects\
            .select_related("survey", "survey__poll")\
            .filter(survey_id=survey_id)\
            .all()
        survey = SurveyPassing.objects.select_related('poll').get(id=survey_id)
        PermissionPollClass.has_query_object_permission(info, survey.poll)

        return ret
