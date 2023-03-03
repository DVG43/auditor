import graphene

from .poll import PollMutation
from .questions import QstnMutation


class Mutation(
    PollMutation,
    QstnMutation,
    graphene.ObjectType
):
    pass

