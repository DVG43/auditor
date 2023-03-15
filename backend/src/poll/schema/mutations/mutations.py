import graphene

from .poll import PollMutation
from .questions import QstnMutation
from .sirveypassing import SurveyPassingMutation


class Mutation(
    PollMutation,
    QstnMutation,
    SurveyPassingMutation,
    graphene.ObjectType
):
    pass
