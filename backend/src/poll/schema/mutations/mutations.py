import graphene

from .poll import PollMutation


class Mutation(PollMutation, graphene.ObjectType):
    pass

