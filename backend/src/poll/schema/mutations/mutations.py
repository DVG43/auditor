import graphene

from .poll import PollMutation
from .questions import QstnMutation
from .surveypassing import SurveyPassingMutation


class Mutation(
    PollMutation,
    QstnMutation,
    SurveyPassingMutation,
    graphene.ObjectType
):
    pass
