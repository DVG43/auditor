import graphene

from .poll import PollMutation
from .questions import QstnMutation
from .surveypassing import SurveyPassingMutation
from .answers import UserAnswerMutation


class Mutation(
    PollMutation,
    QstnMutation,
    SurveyPassingMutation,
    UserAnswerMutation,
    graphene.ObjectType
):
    pass
